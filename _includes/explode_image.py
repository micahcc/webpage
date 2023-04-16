#!/usr/bin/env python3
import json
import shutil
import tempfile
import os
import hashlib
import tarfile
import argparse
import sys
import base64
import random
import string


def _random_string(N):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=N))


def _recursive_build_chain_id(
    diff_id_to_chain_id,
    packed_layer_id_to_diff_id,
    diff_id_to_layer_config,
    packed_self_layer_id,
):
    diff_id = packed_layer_id_to_diff_id[packed_self_layer_id]
    if diff_id in diff_id_to_chain_id:
        return diff_id_to_chain_id[diff_id]

    layer_config = diff_id_to_layer_config[diff_id]
    if "parent" not in layer_config:
        out = diff_id
    else:
        parent_chain_id = _recursive_build_chain_id(
            diff_id_to_chain_id,
            packed_layer_id_to_diff_id,
            diff_id_to_layer_config,
            layer_config["parent"],
        )
        out = compute_sha256_from_string(f"{parent_chain_id} {diff_id}")
        out = f"sha256:{out}"

    diff_id_to_chain_id[diff_id] = out
    return out


def main():
    parser = argparse.ArgumentParser(description="Tool.")
    parser.add_argument(
        "-o",
        "--outdir",
        required=True,
        help="Where to write directory structure",
    )
    parser.add_argument(
        "-i",
        "--input-image",
        nargs="+",
        help="Input image .tar.gz's",
    )

    args = parser.parse_args()

    if os.path.exists(args.outdir):
        print(f"{args.outdir} exists!")
        return 1

    os.makedirs(os.path.join(args.outdir, "image/overlay2/imagedb/content/sha256"))

    for image in args.input_image:
        with tempfile.TemporaryDirectory() as tmpdir:
            image = os.path.abspath(image)
            tar = tarfile.open(image)
            tar.extractall(tmpdir)
            tar.close()

            with open(os.path.join(tmpdir, "manifest.json")) as f:
                manifest = json.load(f)
            #    CONFIG=$(cat manifest.json | jq '.[0].Config' -r)
            #    NAME=$(echo $CONFIG | cut -d '.' -f 1)

            # inside the tar, layers are referred to by an internal ID of
            # unknown origin, we need
            # to map those to sha256 of the layer.tar
            packed_layer_id_to_diff_id = {}
            diff_id_to_cache_id = {}
            diff_id_to_link_id = {}
            for d in os.listdir(tmpdir):
                if not os.path.isdir(os.path.join(tmpdir, d)):
                    continue
                layer_tar = os.path.join(tmpdir, d, "layer.tar")
                layer_sha = compute_sha256(layer_tar)
                diff_id = f"sha256:{layer_sha}"
                packed_layer_id_to_diff_id[d] = diff_id
                link_id = _random_string(26)
                diff_id_to_link_id[diff_id] = link_id
                diff_id_to_cache_id[diff_id] = compute_sha256_from_string(link_id)

            # create lookup table for layer configs
            diff_id_to_layer_config = {}
            for d in os.listdir(tmpdir):
                if not os.path.isdir(os.path.join(tmpdir, d)):
                    continue
                with open(os.path.join(tmpdir, d, "json")) as f:
                    layer_config = json.load(f)
                diff_id_to_layer_config[packed_layer_id_to_diff_id[d]] = layer_config

            # create chain_id for each layer
            # and create lookup for parent diff ids
            diff_id_to_chain_id = {}
            diff_id_to_parent_diff_id = {}
            for d in os.listdir(tmpdir):
                if not os.path.isdir(os.path.join(tmpdir, d)):
                    continue

                diff_id = packed_layer_id_to_diff_id[d]
                config = diff_id_to_layer_config[diff_id]
                if "parent" in config:
                    diff_id_to_parent_diff_id[diff_id] = packed_layer_id_to_diff_id[
                        config["parent"]
                    ]
                else:
                    diff_id_to_parent_diff_id[diff_id] = None

                _recursive_build_chain_id(
                    diff_id_to_chain_id,
                    packed_layer_id_to_diff_id,
                    diff_id_to_layer_config,
                    d,
                )

            image_id = manifest[0]["Config"].split(".")[0]
            image_config_path = os.path.join(
                args.outdir, "image/overlay2/imagedb/content/sha256", image_id
            )
            shutil.copyfile(
                os.path.join(tmpdir, manifest[0]["Config"]), image_config_path
            )

            with open(image_config_path) as f:
                image_config = json.load(f)

            # check validaty of config
            for diff_id in image_config["rootfs"]["diff_ids"]:
                assert diff_id in diff_id_to_layer_config

            for d in os.listdir(tmpdir):
                if not os.path.isdir(os.path.join(tmpdir, d)):
                    continue

                diff_id = packed_layer_id_to_diff_id[d]
                chain_id = diff_id_to_chain_id[diff_id].split(":")[1]

                layer_tar = os.path.join(tmpdir, d, "layer.tar")
                layerdb_dir = os.path.join(
                    args.outdir,
                    "image/overlay2/layerdb/sha256",
                    chain_id,
                )
                os.makedirs(layerdb_dir)

                with open(os.path.join(layerdb_dir, "size"), "w") as f:
                    fsize = os.path.getsize(layer_tar)
                    f.write(f"{fsize}")

                with open(os.path.join(layerdb_dir, "diff"), "w") as f:
                    f.write(diff_id)

                with open(os.path.join(tmpdir, d, "json")) as f:
                    layer_config = json.load(f)

                # remap parent from packed_layer_id_to_diff_id to chain_id
                if "parent" in layer_config:
                    parent = layer_config["parent"]
                    parent_chain_id = diff_id_to_chain_id[
                        packed_layer_id_to_diff_id[parent]
                    ]
                    with open(os.path.join(layerdb_dir, "parent"), "w") as f:
                        f.write(parent_chain_id)

                # generate cache-id
                cache_id = diff_id_to_cache_id[diff_id]
                with open(os.path.join(layerdb_dir, "cache-id"), "w") as f:
                    f.write(cache_id)

                # build overlay dir
                overlay_dir = os.path.join(args.outdir, "overlay2", cache_id)
                os.makedirs(overlay_dir)

                link_dir = os.path.join(args.outdir, "overlay2/l")
                os.makedirs(link_dir, exist_ok=True)

                with open(os.path.join(overlay_dir, "committed"), "w") as f:
                    pass

                # link ID apparently is for Os's that doesn't support long
                # filenames or something
                link_id = diff_id_to_link_id[diff_id]
                with open(os.path.join(overlay_dir, "link"), "w") as f:
                    f.write(link_id)

                # write out lowerdirs
                lower_id = ""
                curr_diff_id = diff_id
                while True:
                    parent_diff_id = diff_id_to_parent_diff_id[curr_diff_id]
                    if parent_diff_id is None:
                        break

                    curr_link_id = diff_id_to_link_id[curr_diff_id]
                    if lower_id == "":
                        lower_id = f"l/{curr_link_id}"
                    else:
                        lower_id = f"{lower_id}:l/{curr_link_id}"
                    curr_diff_id = parent_diff_id

                if lower_id != "":
                    with open(os.path.join(overlay_dir, "lower"), "w") as f:
                        f.write(lower_id)

                tar = tarfile.open(layer_tar)
                tar.extractall(os.path.join(overlay_dir, "diff"))
                tar.close()
                # os.makedirs(os.path.join(overlay_dir, "work/work"))

                old = os.getcwd()
                os.chdir(link_dir)
                os.symlink(
                    f"../{cache_id}/diff",
                    link_id,
                )
                os.chdir(old)

    return 0


def make_link_id(hex_string):
    out_bytes = []
    for i in range(len(hex_string) // 2):
        low = int(hex_string[i * 2], 16)
        if i * 2 + 1 >= len(hex_string):
            up = 0
        else:
            up = int(hex_string[i * 2 + 1], 16)
        n = low + up * 16
        out_bytes.append(n)

    out_bytes = bytes(out_bytes)

    encoded = base64.b32encode(out_bytes).decode("utf-8")

    return encoded[0:26]


def compute_sha256_from_string(s):
    h = hashlib.sha256()
    h.update(s.encode("utf8"))
    return h.hexdigest()


def compute_sha256(fname):
    """Check if the file with the name "filename" matches the SHA-256 sum
    in "expect"."""
    h = hashlib.sha256()
    # This will raise an exception if the file doesn't exist. Catching
    # and handling it is left as an exercise for the reader.
    with open(fname, "rb") as fh:
        # Read and hash the file in 4K chunks. Reading the whole
        # file at once might consume a lot of memory if it is
        # large.
        while True:
            data = fh.read(4096)
            if len(data) == 0:
                break
            else:
                h.update(data)
    return h.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
