# Exploring Docker's on disk layout

All docker state is stored in `/var/lib/docker`, in particular images are stored as
a set of mountable overlay directories.

## On Storage layout

```
image
  + overlay2
    + distribution
    + imagedb # see below
    + layerdb # see below
overlay2 # see below
```

### Top level overlay2 dir

This is of the form:

```
overlay2
  + l
    + LINKID -> ../<CACHE_ID>
  + <CACHE_ID>
    + diff
       + <whole filesytem>
    + committed
    + link
    + lower
    + work
       + work
```

Directory `diff` is just the contents of the layter.tar

Files:

- `committed` is empty
- `lower` contains: `l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU`
- `link` contains `<LINKID>`

where LINKID is random and unique some short code and `CACHE_ID` is random but unique.

```
overlay2
  + l
    + 5VAFOMZUDHZFMSLX2OHRPCWPAJ -> ../d486eecbb911812522fc3f071596b529040abd07c3ac15a9cc72cfb46d8e9c38/diff
    + 6B3RAHVAFPWTGTMDVMFR2J4SK2 -> ../914c07936ddc76ebc5ccc373dc33a75dd07e7b990f6b67ec56b4ba6ae4d630d6/diff
    + 6TZ45A4GZ4S57N5RJD5ZOSIMWY -> ../4272dcce0283c7614e05c0bee3870b3675bb772257e6572462acfa0b7a648a7f/diff
    + FG4YAC4U7LLUV5OGS3W4TFUUBF -> ../ca88b69a3aa5ef096a735c12289d173b1df1406fcd9ac343822d7cfd7fe4bdc7/diff
    + FMV6VHGQTWBBURR2WWMO733ZAU -> ../550c2aa8fc4074bb49c0938f2c7c40473fe8c036a394439ff9ad6a772911cfb7/diff
    + KSVDNX4576JN3GAH47NPJKLQ4X -> ../b2a5746a09cee3a4e8af83458fc5e6b292e439c8cc60e89505a013c6ba46956a/diff
    + LK3UQLPKDWNUNZFLKR6FWGYDCR -> ../c2a3eb2592736d9e0125bcb53b062a706745d07f1de1647609c1930f87bad8fd/diff
    + MECBVOSOQ6JJOIO2S23LFIC5MQ -> ../1ef56f1966660f188b4402d04f0f03efa0dc8974f976d039162db6bdac24ccaa/diff
    + SPTVMQM43OTLJEUHZAOQCO75YK -> ../02300b16e0ebe73e9d1cfacf7a7a8d207e222e38f986e0ec6d7f1ee0a9168a4c/diff
    + TMYDVXFVOFFVSEUZSDYMZTJOLU -> ../856620bec89104b1554054fe63e4d06aaf953fdc11713a3931f29fcfb794eb29/diff
    + UHBZTURYMSPLQUJCWV2KRRSUH5 -> ../3ce35d0caaec37c10742f001a15abc0e623f2697906cee223f62ce8b48b0342e/diff
    + ZQCZ6I2JVCRFXZMXJIVI3DEXAG -> ../847ef282afe912e9b6aab808b477714029e8fbdacaaa39be4d233d54b0ced0b1/diff
  + 02300b16e0ebe73e9d1cfacf7a7a8d207e222e38f986e0ec6d7f1ee0a9168a4c
  + 02300b16e0ebe73e9d1cfacf7a7a8d207e222e38f986e0ec6d7f1ee0a9168a4c
  + 1ef56f1966660f188b4402d04f0f03efa0dc8974f976d039162db6bdac24ccaa
  + 3ce35d0caaec37c10742f001a15abc0e623f2697906cee223f62ce8b48b0342e
  + 4272dcce0283c7614e05c0bee3870b3675bb772257e6572462acfa0b7a648a7f
  + 550c2aa8fc4074bb49c0938f2c7c40473fe8c036a394439ff9ad6a772911cfb7
  + 847ef282afe912e9b6aab808b477714029e8fbdacaaa39be4d233d54b0ced0b1
  + 856620bec89104b1554054fe63e4d06aaf953fdc11713a3931f29fcfb794eb29
  + 914c07936ddc76ebc5ccc373dc33a75dd07e7b990f6b67ec56b4ba6ae4d630d6
  + b2a5746a09cee3a4e8af83458fc5e6b292e439c8cc60e89505a013c6ba46956a
  + c2a3eb2592736d9e0125bcb53b062a706745d07f1de1647609c1930f87bad8fd
  + ca88b69a3aa5ef096a735c12289d173b1df1406fcd9ac343822d7cfd7fe4bdc7
  + d486eecbb911812522fc3f071596b529040abd07c3ac15a9cc72cfb46d8e9c38
     + diff
       + <whole filesystem>
     + work
       + work

```

### Layerdb

```
image
  + overlay2
    + distribution
      + imagedb
        + content
          + sha256
        + metadata
          + sha256
    + layerdb
      + sha256
        + <chain-id>
          + cache-id
          + diff
          + parent
          + size
          + tar-split.json.gz
        + <chain-id>
          ...
      + tmp
```

The files contained in the layer/<cach-id> directory are:

- cache-id: containing the random `cache-id` for the layer
- diff: containing the original layrer's sha256, in the format: `sha256:<sha256>`
- parent: containing the parent's `chain-id` (`sha256("<parent_chain_id> <self_diff_id>")`)
- size: Size of the layer.tar file in bytes
- tar-split.json.gz (just an optimization, we can ignore)

Example:

```
image
  + overlay2
    + distribution
      + imagedb
        + content
          + sha256
        + metadata
          + sha256
    + layerdb
      + sha256
        + 050b9292b1c4ef859bc947f450e68b41ee69c6956040328cb917e8fec63ec2dd
        + 25cdbcfc7a09f3381904680ace956b1e2e06c50f70b04c6f5e950c8003aa22c0
        + 518fdaf2a9e0f3be357d08a342dd39aedbb262f7aa5863ef2f43ceaad17e23b7
        + 6d9a462062afe70a347f2f0f21162eded332757ec8443624a1e5314cfec28e5a
        + 8db8f53f4914863a3a8c1a64482dd3ca5e960c3c8d2cf5cd82f81b6c5c32b3a7
        + 94440a7f3983a2996c5221922f3693d61933db82f2196b55ee6b92ef390735a0
        + b321e8877295f400ca8cc95ca1af92c8c6440e9675a8766ecccc60d81c69fb37
        + b741310eed6f050b486dae5427b31da464ef176963a6f85b6a38e1a90ac5323b
        + bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1
        + da898a2e1b3213abf533c13aed412487af8370de7b77ec31f5334113edcc144b
        + dffdb30cad9ada86a0d504cbb8466ebfbb5fb112338da9a2aaa0b2dba1ee2535
        + f8856a4c49ca60c23e6c7f60f8dc17f1f2e05e00c313947a58f05e37279d5055
      + tmp
```

### Imagedb

```
image/overlay2/imagedb/content/
 + sha256
    + 19d027b65340e931103d2e05c1658bf78fd81f3913bb8deacbe1a49b6e98b77f
```

This file contains the original `<image_id>.json` stored in the tar.

## Image Tar Layout

Exported images are of the form:

```
<layer>/VERSION
<layer>/json
<layer>/layer.tar
<image_id>.json
manifest.json
repositories
```

- VERSION is just versioning information for the package format and can be ignored.
- The random sha256 `<layer>` are referenced by "parent" in each layers json file

```
micahc@tyche /tmp/unpack  $ cat 19d027b65340e931103d2e05c1658bf78fd81f3913bb8deacbe1a49b6e98b77f.json | jq
{
  "architecture": "amd64",
  "author": "Régis Belson <me@regisbelson.fr>",
  "config": {
    "Hostname": "",
    "Domainname": "",
    "User": "",
    "AttachStdin": false,
    "AttachStdout": false,
    "AttachStderr": false,
    "ExposedPorts": {
      "5432/tcp": {}
    },
    "Tty": false,
    "OpenStdin": false,
    "StdinOnce": false,
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "LANG=en_US.utf8",
      "PG_MAJOR=10",
      "PG_VERSION=10.7",
      "PG_SHA256=bfed1065380c1bba927bfe51f23168471373f26e3324cbad859269cc32733ede",
      "PGDATA=/var/lib/postgresql/data",
      "POSTGIS_VERSION=2.5.2",
      "POSTGIS_SHA256=225aeaece00a1a6a9af15526af81bef2af27f4c198de820af1367a792ee1d1a9"
    ],
    "Cmd": [
      "postgres"
    ],
    "ArgsEscaped": true,
    "Image": "sha256:4f2dfa983c659af2cbd0a136ef96e0937d35f3a019917e683f80d3e56623a3ab",
    "Volumes": {
      "/var/lib/postgresql/data": {}
    },
    "WorkingDir": "",
    "Entrypoint": [
      "docker-entrypoint.sh"
    ],
    "OnBuild": null,
    "Labels": null
  },
  "container_config": {
    "Hostname": "",
    "Domainname": "",
    "User": "",
    "AttachStdin": false,
    "AttachStdout": false,
    "AttachStderr": false,
    "ExposedPorts": {
      "5432/tcp": {}
    },
    "Tty": false,
    "OpenStdin": false,
    "StdinOnce": false,
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "LANG=en_US.utf8",
      "PG_MAJOR=10",
      "PG_VERSION=10.7",
      "PG_SHA256=bfed1065380c1bba927bfe51f23168471373f26e3324cbad859269cc32733ede",
      "PGDATA=/var/lib/postgresql/data",
      "POSTGIS_VERSION=2.5.2",
      "POSTGIS_SHA256=225aeaece00a1a6a9af15526af81bef2af27f4c198de820af1367a792ee1d1a9"
    ],
    "Cmd": [
      "/bin/sh",
      "-c",
      "#(nop) COPY file:df54368b03fe867c8130a8de726618c6f81123abf089de637f821b556718cb53 in /usr/local/bin "
    ],
    "ArgsEscaped": true,
    "Image": "sha256:4f2dfa983c659af2cbd0a136ef96e0937d35f3a019917e683f80d3e56623a3ab",
    "Volumes": {
      "/var/lib/postgresql/data": {}
    },
    "WorkingDir": "",
    "Entrypoint": [
      "docker-entrypoint.sh"
    ],
    "OnBuild": null,
    "Labels": null
  },
  "created": "2019-03-21T02:49:48.543104211Z",
  "docker_version": "18.03.1-ee-3",
  "history": [
    {
      "created": "2019-03-07T22:19:40.113750514Z",
      "created_by": "/bin/sh -c #(nop) ADD file:88875982b0512a9d0ba001bfea19497ae9a9442c257b19c61bffc56e7201b0c3 in / "
    },
    {
      "created": "2019-03-07T22:19:40.247110971Z",
      "created_by": "/bin/sh -c #(nop)  CMD [\"/bin/sh\"]",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:17:17.856985414Z",
      "created_by": "/bin/sh -c set -ex; \tpostgresHome=\"$(getent passwd postgres)\"; \tpostgresHome=\"$(echo \"$postgresHome\" | cut -d: -f6)\"; \t[ \"$postgresHome\" = '/var/lib/postgresql' ]; \tmkdir -p \"$postgresHome\"; \tchown -R postgres:postgres \"$postgresHome\""
    },
    {
      "created": "2019-03-08T02:17:18.247250729Z",
      "created_by": "/bin/sh -c #(nop)  ENV LANG=en_US.utf8",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:17:19.804033293Z",
      "created_by": "/bin/sh -c mkdir /docker-entrypoint-initdb.d"
    },
    {
      "created": "2019-03-08T02:22:51.450873815Z",
      "created_by": "/bin/sh -c #(nop)  ENV PG_MAJOR=10",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:22:51.691344162Z",
      "created_by": "/bin/sh -c #(nop)  ENV PG_VERSION=10.7",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:22:51.979397404Z",
      "created_by": "/bin/sh -c #(nop)  ENV PG_SHA256=bfed1065380c1bba927bfe51f23168471373f26e3324cbad859269cc32733ede",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:28:26.845291126Z",
      "created_by": "/bin/sh -c set -ex \t\t&& apk add --no-cache --virtual .fetch-deps \t\tca-certificates \t\topenssl \t\ttar \t\t&& wget -O postgresql.tar.bz2 \"https://ftp.postgresql.org/pub/source/v$PG_VERSION/postgresql-$PG_VERSION.tar.bz2\" \t&& echo \"$PG_SHA256 *postgresql.tar.bz2\" | sha256sum -c - \t&& mkdir -p /usr/src/postgresql \t&& tar \t\t--extract \t\t--file postgresql.tar.bz2 \t\t--directory /usr/src/postgresql \t\t--strip-components 1 \t&& rm postgresql.tar.bz2 \t\t&& apk add --no-cache --virtual .build-deps \t\tbison \t\tcoreutils \t\tdpkg-dev dpkg \t\tflex \t\tgcc \t\tlibc-dev \t\tlibedit-dev \t\tlibxml2-dev \t\tlibxslt-dev \t\tmake \t\topenssl-dev \t\tperl-utils \t\tperl-ipc-run \t\tutil-linux-dev \t\tzlib-dev \t\ticu-dev \t\t&& cd /usr/src/postgresql \t&& awk '$1 == \"#define\" && $2 == \"DEFAULT_PGSOCKET_DIR\" && $3 == \"\\\"/tmp\\\"\" { $3 = \"\\\"/var/run/postgresql\\\"\"; print; next } { print }' src/include/pg_config_manual.h > src/include/pg_config_manual.h.new \t&& grep '/var/run/postgresql' src/include/pg_config_manual.h.new \t&& mv src/include/pg_config_manual.h.new src/include/pg_config_manual.h \t&& gnuArch=\"$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)\" \t&& wget -O config/config.guess 'https://git.savannah.gnu.org/cgit/config.git/plain/config.guess?id=7d3d27baf8107b630586c962c057e22149653deb' \t&& wget -O config/config.sub 'https://git.savannah.gnu.org/cgit/config.git/plain/config.sub?id=7d3d27baf8107b630586c962c057e22149653deb' \t&& ./configure \t\t--build=\"$gnuArch\" \t\t--enable-integer-datetimes \t\t--enable-thread-safety \t\t--enable-tap-tests \t\t--disable-rpath \t\t--with-uuid=e2fs \t\t--with-gnu-ld \t\t--with-pgport=5432 \t\t--with-system-tzdata=/usr/share/zoneinfo \t\t--prefix=/usr/local \t\t--with-includes=/usr/local/include \t\t--with-libraries=/usr/local/lib \t\t\t\t--with-openssl \t\t--with-libxml \t\t--with-libxslt \t\t--with-icu \t&& make -j \"$(nproc)\" world \t&& make install-world \t&& make -C contrib install \t\t&& runDeps=\"$( \t\tscanelf --needed --nobanner --format '%n#p' --recursive /usr/local \t\t\t| tr ',' '\\n' \t\t\t| sort -u \t\t\t| awk 'system(\"[ -e /usr/local/lib/\" $1 \" ]\") == 0 { next } { print \"so:\" $1 }' \t)\" \t&& apk add --no-cache --virtual .postgresql-rundeps \t\t$runDeps \t\tbash \t\tsu-exec \t\ttzdata \t&& apk del .fetch-deps .build-deps \t&& cd / \t&& rm -rf \t\t/usr/src/postgresql \t\t/usr/local/share/doc \t\t/usr/local/share/man \t&& find /usr/local -name '*.a' -delete"
    },
    {
      "created": "2019-03-08T02:28:27.666798482Z",
      "created_by": "/bin/sh -c sed -ri \"s!^#?(listen_addresses)\\s*=\\s*\\S+.*!\\1 = '*'!\" /usr/local/share/postgresql/postgresql.conf.sample"
    },
    {
      "created": "2019-03-08T02:28:28.371666184Z",
      "created_by": "/bin/sh -c mkdir -p /var/run/postgresql && chown -R postgres:postgres /var/run/postgresql && chmod 2777 /var/run/postgresql"
    },
    {
      "created": "2019-03-08T02:28:28.542491858Z",
      "created_by": "/bin/sh -c #(nop)  ENV PGDATA=/var/lib/postgresql/data",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:28:29.283654682Z",
      "created_by": "/bin/sh -c mkdir -p \"$PGDATA\" && chown -R postgres:postgres \"$PGDATA\" && chmod 777 \"$PGDATA\" # this 777 will be replaced by 700 at runtime (allows semi-arbitrary \"--user\" values)"
    },
    {
      "created": "2019-03-08T02:28:29.455284096Z",
      "created_by": "/bin/sh -c #(nop)  VOLUME [/var/lib/postgresql/data]",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:28:29.6357586Z",
      "created_by": "/bin/sh -c #(nop) COPY file:06aacea0082744225fdd508b7ef4d5280ad1b35ec665f4399894e8fd2cfd37ad in /usr/local/bin/ "
    },
    {
      "created": "2019-03-08T02:28:30.343946016Z",
      "created_by": "/bin/sh -c ln -s usr/local/bin/docker-entrypoint.sh / # backwards compat"
    },
    {
      "created": "2019-03-08T02:28:30.510992247Z",
      "created_by": "/bin/sh -c #(nop)  ENTRYPOINT [\"docker-entrypoint.sh\"]",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:28:30.683540298Z",
      "created_by": "/bin/sh -c #(nop)  EXPOSE 5432",
      "empty_layer": true
    },
    {
      "created": "2019-03-08T02:28:30.835196397Z",
      "created_by": "/bin/sh -c #(nop)  CMD [\"postgres\"]",
      "empty_layer": true
    },
    {
      "created": "2019-03-21T02:41:52.393112684Z",
      "author": "Régis Belson <me@regisbelson.fr>",
      "created_by": "/bin/sh -c #(nop)  MAINTAINER Régis Belson <me@regisbelson.fr>",
      "empty_layer": true
    },
    {
      "created": "2019-03-21T02:41:52.761404586Z",
      "author": "Régis Belson <me@regisbelson.fr>",
      "created_by": "/bin/sh -c #(nop)  ENV POSTGIS_VERSION=2.5.2",
      "empty_layer": true
    },
    {
      "created": "2019-03-21T02:41:53.221336101Z",
      "author": "Régis Belson <me@regisbelson.fr>",
      "created_by": "/bin/sh -c #(nop)  ENV POSTGIS_SHA256=225aeaece00a1a6a9af15526af81bef2af27f4c198de820af1367a792ee1d1a9",
      "empty_layer": true
    },
    {
      "created": "2019-03-21T02:49:47.440925426Z",
      "author": "Régis Belson <me@regisbelson.fr>",
      "created_by": "/bin/sh -c set -ex         && apk add --no-cache --virtual .fetch-deps         ca-certificates         openssl         tar         && wget -O postgis.tar.gz \"https://github.com/postgis/postgis/archive/$POSTGIS_VERSION.tar.gz\"     && echo \"$POSTGIS_SHA256 *postgis.tar.gz\" | sha256sum -c -     && mkdir -p /usr/src/postgis     && tar         --extract         --file postgis.tar.gz         --directory /usr/src/postgis         --strip-components 1     && rm postgis.tar.gz         && apk add --no-cache --virtual .build-deps         autoconf         automake         g++         json-c-dev         libtool         libxml2-dev         make         perl         && apk add --no-cache --virtual .build-deps-edge         --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing         --repository http://dl-cdn.alpinelinux.org/alpine/edge/main         gdal-dev         geos-dev         proj4-dev         protobuf-c-dev     && cd /usr/src/postgis     && ./autogen.sh     && ./configure     && make     && make install     && apk add --no-cache --virtual .postgis-rundeps         json-c     && apk add --no-cache --virtual .postgis-rundeps-edge         --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing         --repository http://dl-cdn.alpinelinux.org/alpine/edge/main         geos         gdal         proj4         protobuf-c     && cd /     && rm -rf /usr/src/postgis     && apk del .fetch-deps .build-deps .build-deps-edge"
    },
    {
      "created": "2019-03-21T02:49:48.003198557Z",
      "author": "Régis Belson <me@regisbelson.fr>",
      "created_by": "/bin/sh -c #(nop) COPY file:3e32231cab79cf77ec80910221df7885cfc6987a009998ebf6599fe15791ac5f in /docker-entrypoint-initdb.d/postgis.sh "
    },
    {
      "created": "2019-03-21T02:49:48.543104211Z",
      "author": "Régis Belson <me@regisbelson.fr>",
      "created_by": "/bin/sh -c #(nop) COPY file:df54368b03fe867c8130a8de726618c6f81123abf089de637f821b556718cb53 in /usr/local/bin "
    }
  ],
  "os": "linux",
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1",
      "sha256:ff054d77d76e8379153982cb36a5f62994e831638b84015eac3877b9671f6cc4",
      "sha256:9af3018fb20d9be01781803b6682fc715845ad3e089c7a86396ac3c8553cffd2",
      "sha256:d3d5265b5cbb41efd331dd10928d9790334a9617605ce7ad6fe4b71dffb1418d",
      "sha256:65df989e535eb5064b3e7ab0d92f60c385494c2408558368babb5351f7c5d377",
      "sha256:fd7aebb349a8e7a2ca1ab566119e13f67723b2160c17a4f19353a0bcb3f3ed0e",
      "sha256:ca63742794eba253d2e6e62634279c94f6ceba499e0ff38460acf6748390ea02",
      "sha256:736f3ed84a048128949fc6ebe6cec518814cf3133c6286f5f8bfbe718d82d691",
      "sha256:b9062085ff004e91d32a1d3d591ac48c27f769cd8a8264d3864e6452b531c565",
      "sha256:ff9074ae66c13c2c5db1f9d1975802a1bd4b62d0352a49637aee77a07725531a",
      "sha256:517a85b54673a1f3469fa20e0796f29b303c5d9bf4024df1e0a9b568fa665ca9",
      "sha256:ce2a404fe1f336cf533ea1dc362792d2eed1e5c0cb28422aa13ba8c5d2037ab6"
    ]
  }
}
```

```
[root@tyche docker]# find -name 'size' | while read line; do echo $line; cat $line; echo ''; done
./image/overlay2/layerdb/sha256/f8856a4c49ca60c23e6c7f60f8dc17f1f2e05e00c313947a58f05e37279d5055/size
22746
./image/overlay2/layerdb/sha256/bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1/size
5524769
./image/overlay2/layerdb/sha256/6d9a462062afe70a347f2f0f21162eded332757ec8443624a1e5314cfec28e5a/size
65176718
./image/overlay2/layerdb/sha256/050b9292b1c4ef859bc947f450e68b41ee69c6956040328cb917e8fec63ec2dd/size
5466
./image/overlay2/layerdb/sha256/25cdbcfc7a09f3381904680ace956b1e2e06c50f70b04c6f5e950c8003aa22c0/size
0
./image/overlay2/layerdb/sha256/94440a7f3983a2996c5221922f3693d61933db82f2196b55ee6b92ef390735a0/size
1045
./image/overlay2/layerdb/sha256/da898a2e1b3213abf533c13aed412487af8370de7b77ec31f5334113edcc144b/size
0
./image/overlay2/layerdb/sha256/dffdb30cad9ada86a0d504cbb8466ebfbb5fb112338da9a2aaa0b2dba1ee2535/size
0
./image/overlay2/layerdb/sha256/b321e8877295f400ca8cc95ca1af92c8c6440e9675a8766ecccc60d81c69fb37/size
0
./image/overlay2/layerdb/sha256/518fdaf2a9e0f3be357d08a342dd39aedbb262f7aa5863ef2f43ceaad17e23b7/size
0
./image/overlay2/layerdb/sha256/b741310eed6f050b486dae5427b31da464ef176963a6f85b6a38e1a90ac5323b/size
680
./image/overlay2/layerdb/sha256/8db8f53f4914863a3a8c1a64482dd3ca5e960c3c8d2cf5cd82f81b6c5c32b3a7/size
75498712
```

```
$ tar tvf myimage.tar.gz
drwxr-xr-x 0/0 0 2019-03-20 19:49 04e944734ed89a763d4ae1110f4527167af8baa583655491c9bb5694ac23c1f1/
-rw-r--r-- 0/0 3 2019-03-20 19:49 04e944734ed89a763d4ae1110f4527167af8baa583655491c9bb5694ac23c1f1/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 04e944734ed89a763d4ae1110f4527167af8baa583655491c9bb5694ac23c1f1/json
-rw-r--r-- 0/0 68893184 2019-03-20 19:49 04e944734ed89a763d4ae1110f4527167af8baa583655491c9bb5694ac23c1f1/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 167f732e44357c03c8e8ea994db4451e8e9057d0b4856379fa127129bd81e455/
-rw-r--r-- 0/0 3 2019-03-20 19:49 167f732e44357c03c8e8ea994db4451e8e9057d0b4856379fa127129bd81e455/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 167f732e44357c03c8e8ea994db4451e8e9057d0b4856379fa127129bd81e455/json
-rw-r--r-- 0/0 2560 2019-03-20 19:49 167f732e44357c03c8e8ea994db4451e8e9057d0b4856379fa127129bd81e455/layer.tar
-rw-r--r-- 0/0 11239 2019-03-20 19:49 19d027b65340e931103d2e05c1658bf78fd81f3913bb8deacbe1a49b6e98b77f.json
drwxr-xr-x 0/0 0 2019-03-20 19:49 21dc88f6034c70b0bf2b904a11fad60696263324c8e19970fbbf6af9b9e65b0d/
-rw-r--r-- 0/0 3 2019-03-20 19:49 21dc88f6034c70b0bf2b904a11fad60696263324c8e19970fbbf6af9b9e65b0d/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 21dc88f6034c70b0bf2b904a11fad60696263324c8e19970fbbf6af9b9e65b0d/json
-rw-r--r-- 0/0 8704 2019-03-20 19:49 21dc88f6034c70b0bf2b904a11fad60696263324c8e19970fbbf6af9b9e65b0d/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 2fe535a6750cbba498c43bb665fd12f18d97e3d5252ae99a796583a705f7f2bc/
-rw-r--r-- 0/0 3 2019-03-20 19:49 2fe535a6750cbba498c43bb665fd12f18d97e3d5252ae99a796583a705f7f2bc/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 2fe535a6750cbba498c43bb665fd12f18d97e3d5252ae99a796583a705f7f2bc/json
-rw-r--r-- 0/0 3072 2019-03-20 19:49 2fe535a6750cbba498c43bb665fd12f18d97e3d5252ae99a796583a705f7f2bc/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 3a882721e2f7fd6b70e63d17cb08f547b9963a2fcde5b67f139c4a64d6efe1e1/
-rw-r--r-- 0/0 3 2019-03-20 19:49 3a882721e2f7fd6b70e63d17cb08f547b9963a2fcde5b67f139c4a64d6efe1e1/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 3a882721e2f7fd6b70e63d17cb08f547b9963a2fcde5b67f139c4a64d6efe1e1/json
-rw-r--r-- 0/0 26624 2019-03-20 19:49 3a882721e2f7fd6b70e63d17cb08f547b9963a2fcde5b67f139c4a64d6efe1e1/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 45fe957375aecccdc9902d99ecc17a28940b8d0dfcc065d9f1b4b2c33c309cc8/
-rw-r--r-- 0/0 3 2019-03-20 19:49 45fe957375aecccdc9902d99ecc17a28940b8d0dfcc065d9f1b4b2c33c309cc8/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 45fe957375aecccdc9902d99ecc17a28940b8d0dfcc065d9f1b4b2c33c309cc8/json
-rw-r--r-- 0/0 1536 2019-03-20 19:49 45fe957375aecccdc9902d99ecc17a28940b8d0dfcc065d9f1b4b2c33c309cc8/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 4d91f57cd3540a73bcf63a41ad0a5f8932c2257a97b2a20f43cca879ee72ebf8/
-rw-r--r-- 0/0 3 2019-03-20 19:49 4d91f57cd3540a73bcf63a41ad0a5f8932c2257a97b2a20f43cca879ee72ebf8/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 4d91f57cd3540a73bcf63a41ad0a5f8932c2257a97b2a20f43cca879ee72ebf8/json
-rw-r--r-- 0/0 1536 2019-03-20 19:49 4d91f57cd3540a73bcf63a41ad0a5f8932c2257a97b2a20f43cca879ee72ebf8/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 50659a5fb576331c2a94226ddb11ab95d5f7b9cc972975458796d15aae34807f/
-rw-r--r-- 0/0 3 2019-03-20 19:49 50659a5fb576331c2a94226ddb11ab95d5f7b9cc972975458796d15aae34807f/VERSION
-rw-r--r-- 0/0 1992 2019-03-20 19:49 50659a5fb576331c2a94226ddb11ab95d5f7b9cc972975458796d15aae34807f/json
-rw-r--r-- 0/0 4608 2019-03-20 19:49 50659a5fb576331c2a94226ddb11ab95d5f7b9cc972975458796d15aae34807f/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 6f749379d19b0ace9aab81a7ac0abe53f74084bda8f25dbe7795e99499133466/
-rw-r--r-- 0/0 3 2019-03-20 19:49 6f749379d19b0ace9aab81a7ac0abe53f74084bda8f25dbe7795e99499133466/VERSION
-rw-r--r-- 0/0 406 2019-03-20 19:49 6f749379d19b0ace9aab81a7ac0abe53f74084bda8f25dbe7795e99499133466/json
-rw-r--r-- 0/0 5792256 2019-03-20 19:49 6f749379d19b0ace9aab81a7ac0abe53f74084bda8f25dbe7795e99499133466/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 81cd805fb4f775dd97dc3b6fee85755493bf42755886c0bd93af22a5c1d61e34/
-rw-r--r-- 0/0 3 2019-03-20 19:49 81cd805fb4f775dd97dc3b6fee85755493bf42755886c0bd93af22a5c1d61e34/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 81cd805fb4f775dd97dc3b6fee85755493bf42755886c0bd93af22a5c1d61e34/json
-rw-r--r-- 0/0 3072 2019-03-20 19:49 81cd805fb4f775dd97dc3b6fee85755493bf42755886c0bd93af22a5c1d61e34/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 853ebac8e5df8260e8df5f64ae0af37719a5ba35f0b3a3707a6a4027df55f93d/
-rw-r--r-- 0/0 3 2019-03-20 19:49 853ebac8e5df8260e8df5f64ae0af37719a5ba35f0b3a3707a6a4027df55f93d/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 853ebac8e5df8260e8df5f64ae0af37719a5ba35f0b3a3707a6a4027df55f93d/json
-rw-r--r-- 0/0 76058112 2019-03-20 19:49 853ebac8e5df8260e8df5f64ae0af37719a5ba35f0b3a3707a6a4027df55f93d/layer.tar
drwxr-xr-x 0/0 0 2019-03-20 19:49 df55bef7c463c245fd24b375b9d0083f1da937f3da6060e20d5c9e6a0d996be8/
-rw-r--r-- 0/0 3 2019-03-20 19:49 df55bef7c463c245fd24b375b9d0083f1da937f3da6060e20d5c9e6a0d996be8/VERSION
-rw-r--r-- 0/0 482 2019-03-20 19:49 df55bef7c463c245fd24b375b9d0083f1da937f3da6060e20d5c9e6a0d996be8/json
-rw-r--r-- 0/0 2048 2019-03-20 19:49 df55bef7c463c245fd24b375b9d0083f1da937f3da6060e20d5c9e6a0d996be8/layer.tar
-rw-r--r-- 0/0 1061 1969-12-31 16:00 manifest.json
-rw-r--r-- 0/0 101 1969-12-31 16:00 repositories
```

Note that XXX has no real use in:

```
XXX/VERSION
XXX/json
XXX/layer.tar
```

- The sha256 of `XXX/layer.tar` is used as the `<diff>` in the output layout

```
$ cat image/overlay2/layerdb/sha256/<CHAIN_ID>/diff
sha256:<diff>
```

- `<chain-id>` is `<diff>` if there is no parent, if there is a parent its: `<`

```
$ cat ./image/overlay2/layerdb/sha256/f8856a4c49ca60c23e6c7f60f8dc17f1f2e05e00c313947a58f05e37279d5055/parent
sha256:6d9a462062afe70a347f2f0f21162eded332757ec8443624a1e5314cfec28e5a
$ cat ./image/overlay2/layerdb/sha256/6d9a462062afe70a347f2f0f21162eded332757ec8443624a1e5314cfec28e5a/parent
sha256:b321e8877295f400ca8cc95ca1af92c8c6440e9675a8766ecccc60d81c69fb37
$ cat ./image/overlay2/layerdb/sha256/050b9292b1c4ef859bc947f450e68b41ee69c6956040328cb917e8fec63ec2dd/parent
sha256:25cdbcfc7a09f3381904680ace956b1e2e06c50f70b04c6f5e950c8003aa22c0
$ cat ./image/overlay2/layerdb/sha256/25cdbcfc7a09f3381904680ace956b1e2e06c50f70b04c6f5e950c8003aa22c0/parent
sha256:da898a2e1b3213abf533c13aed412487af8370de7b77ec31f5334113edcc144b
$ cat ./image/overlay2/layerdb/sha256/94440a7f3983a2996c5221922f3693d61933db82f2196b55ee6b92ef390735a0/parent
sha256:b741310eed6f050b486dae5427b31da464ef176963a6f85b6a38e1a90ac5323b
$ cat ./image/overlay2/layerdb/sha256/da898a2e1b3213abf533c13aed412487af8370de7b77ec31f5334113edcc144b/parent
sha256:f8856a4c49ca60c23e6c7f60f8dc17f1f2e05e00c313947a58f05e37279d5055
$ cat ./image/overlay2/layerdb/sha256/dffdb30cad9ada86a0d504cbb8466ebfbb5fb112338da9a2aaa0b2dba1ee2535/parent
sha256:050b9292b1c4ef859bc947f450e68b41ee69c6956040328cb917e8fec63ec2dd
$ cat ./image/overlay2/layerdb/sha256/b321e8877295f400ca8cc95ca1af92c8c6440e9675a8766ecccc60d81c69fb37/parent
sha256:518fdaf2a9e0f3be357d08a342dd39aedbb262f7aa5863ef2f43ceaad17e23b7
$ cat ./image/overlay2/layerdb/sha256/518fdaf2a9e0f3be357d08a342dd39aedbb262f7aa5863ef2f43ceaad17e23b7/parent
sha256:bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1
$ cat ./image/overlay2/layerdb/sha256/b741310eed6f050b486dae5427b31da464ef176963a6f85b6a38e1a90ac5323b/parent
sha256:8db8f53f4914863a3a8c1a64482dd3ca5e960c3c8d2cf5cd82f81b6c5c32b3a7
$ cat ./image/overlay2/layerdb/sha256/8db8f53f4914863a3a8c1a64482dd3ca5e960c3c8d2cf5cd82f81b6c5c32b3a7/parent
sha256:dffdb30cad9ada86a0d504cbb8466ebfbb5fb112338da9a2aaa0b2dba1ee2535
```

```
micahc@tyche /tmp/unpack $ sha256sum \*/layer.tar
d3d5265b5cbb41efd331dd10928d9790334a9617605ce7ad6fe4b71dffb1418d 04e944734ed89a763d4ae1110f4527167af8baa583655491c9bb5694ac23c1f1/layer.tar
ff054d77d76e8379153982cb36a5f62994e831638b84015eac3877b9671f6cc4 167f732e44357c03c8e8ea994db4451e8e9057d0b4856379fa127129bd81e455/layer.tar
736f3ed84a048128949fc6ebe6cec518814cf3133c6286f5f8bfbe718d82d691 21dc88f6034c70b0bf2b904a11fad60696263324c8e19970fbbf6af9b9e65b0d/layer.tar
ca63742794eba253d2e6e62634279c94f6ceba499e0ff38460acf6748390ea02 2fe535a6750cbba498c43bb665fd12f18d97e3d5252ae99a796583a705f7f2bc/layer.tar
65df989e535eb5064b3e7ab0d92f60c385494c2408558368babb5351f7c5d377 3a882721e2f7fd6b70e63d17cb08f547b9963a2fcde5b67f139c4a64d6efe1e1/layer.tar
b9062085ff004e91d32a1d3d591ac48c27f769cd8a8264d3864e6452b531c565 45fe957375aecccdc9902d99ecc17a28940b8d0dfcc065d9f1b4b2c33c309cc8/layer.tar
9af3018fb20d9be01781803b6682fc715845ad3e089c7a86396ac3c8553cffd2 4d91f57cd3540a73bcf63a41ad0a5f8932c2257a97b2a20f43cca879ee72ebf8/layer.tar
ce2a404fe1f336cf533ea1dc362792d2eed1e5c0cb28422aa13ba8c5d2037ab6 50659a5fb576331c2a94226ddb11ab95d5f7b9cc972975458796d15aae34807f/layer.tar
bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1 6f749379d19b0ace9aab81a7ac0abe53f74084bda8f25dbe7795e99499133466/layer.tar
517a85b54673a1f3469fa20e0796f29b303c5d9bf4024df1e0a9b568fa665ca9 81cd805fb4f775dd97dc3b6fee85755493bf42755886c0bd93af22a5c1d61e34/layer.tar
ff9074ae66c13c2c5db1f9d1975802a1bd4b62d0352a49637aee77a07725531a 853ebac8e5df8260e8df5f64ae0af37719a5ba35f0b3a3707a6a4027df55f93d/layer.tar
fd7aebb349a8e7a2ca1ab566119e13f67723b2160c17a4f19353a0bcb3f3ed0e df55bef7c463c245fd24b375b9d0083f1da937f3da6060e20d5c9e6a0d996be8/layer.tar

```

```

$ cat ./image/overlay2/layerdb/sha256/f8856a4c49ca60c23e6c7f60f8dc17f1f2e05e00c313947a58f05e37279d5055/diff
sha256:65df989e535eb5064b3e7ab0d92f60c385494c2408558368babb5351f7c5d377
$ cat ./image/overlay2/layerdb/sha256/bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1/diff
sha256:bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1
$ cat ./image/overlay2/layerdb/sha256/6d9a462062afe70a347f2f0f21162eded332757ec8443624a1e5314cfec28e5a/diff
sha256:d3d5265b5cbb41efd331dd10928d9790334a9617605ce7ad6fe4b71dffb1418d
$ cat ./image/overlay2/layerdb/sha256/050b9292b1c4ef859bc947f450e68b41ee69c6956040328cb917e8fec63ec2dd/diff
sha256:736f3ed84a048128949fc6ebe6cec518814cf3133c6286f5f8bfbe718d82d691
$ cat ./image/overlay2/layerdb/sha256/25cdbcfc7a09f3381904680ace956b1e2e06c50f70b04c6f5e950c8003aa22c0/diff
sha256:ca63742794eba253d2e6e62634279c94f6ceba499e0ff38460acf6748390ea02
$ cat ./image/overlay2/layerdb/sha256/94440a7f3983a2996c5221922f3693d61933db82f2196b55ee6b92ef390735a0/diff
sha256:ce2a404fe1f336cf533ea1dc362792d2eed1e5c0cb28422aa13ba8c5d2037ab6
$ cat ./image/overlay2/layerdb/sha256/da898a2e1b3213abf533c13aed412487af8370de7b77ec31f5334113edcc144b/diff
sha256:fd7aebb349a8e7a2ca1ab566119e13f67723b2160c17a4f19353a0bcb3f3ed0e
$ cat ./image/overlay2/layerdb/sha256/dffdb30cad9ada86a0d504cbb8466ebfbb5fb112338da9a2aaa0b2dba1ee2535/diff
sha256:b9062085ff004e91d32a1d3d591ac48c27f769cd8a8264d3864e6452b531c565
$ cat ./image/overlay2/layerdb/sha256/b321e8877295f400ca8cc95ca1af92c8c6440e9675a8766ecccc60d81c69fb37/diff
sha256:9af3018fb20d9be01781803b6682fc715845ad3e089c7a86396ac3c8553cffd2
$ cat ./image/overlay2/layerdb/sha256/518fdaf2a9e0f3be357d08a342dd39aedbb262f7aa5863ef2f43ceaad17e23b7/diff
sha256:ff054d77d76e8379153982cb36a5f62994e831638b84015eac3877b9671f6cc4
$ cat ./image/overlay2/layerdb/sha256/b741310eed6f050b486dae5427b31da464ef176963a6f85b6a38e1a90ac5323b/diff
sha256:517a85b54673a1f3469fa20e0796f29b303c5d9bf4024df1e0a9b568fa665ca9
$ cat ./image/overlay2/layerdb/sha256/8db8f53f4914863a3a8c1a64482dd3ca5e960c3c8d2cf5cd82f81b6c5c32b3a7/diff
sha256:ff9074ae66c13c2c5db1f9d1975802a1bd4b62d0352a49637aee77a07725531a

```

```

$ cat ./image/overlay2/layerdb/sha256/f8856a4c49ca60c23e6c7f60f8dc17f1f2e05e00c313947a58f05e37279d5055/cache-id
d486eecbb911812522fc3f071596b529040abd07c3ac15a9cc72cfb46d8e9c38
$ cat ./image/overlay2/layerdb/sha256/bcf2f368fe234217249e00ad9d762d8f1a3156d60c442ed92079fa5b120634a1/cache-id
856620bec89104b1554054fe63e4d06aaf953fdc11713a3931f29fcfb794eb29
$ cat ./image/overlay2/layerdb/sha256/6d9a462062afe70a347f2f0f21162eded332757ec8443624a1e5314cfec28e5a/cache-id
847ef282afe912e9b6aab808b477714029e8fbdacaaa39be4d233d54b0ced0b1
$ cat ./image/overlay2/layerdb/sha256/050b9292b1c4ef859bc947f450e68b41ee69c6956040328cb917e8fec63ec2dd/cache-id
02300b16e0ebe73e9d1cfacf7a7a8d207e222e38f986e0ec6d7f1ee0a9168a4c
$ cat ./image/overlay2/layerdb/sha256/25cdbcfc7a09f3381904680ace956b1e2e06c50f70b04c6f5e950c8003aa22c0/cache-id
c2a3eb2592736d9e0125bcb53b062a706745d07f1de1647609c1930f87bad8fd
$ cat ./image/overlay2/layerdb/sha256/94440a7f3983a2996c5221922f3693d61933db82f2196b55ee6b92ef390735a0/cache-id
914c07936ddc76ebc5ccc373dc33a75dd07e7b990f6b67ec56b4ba6ae4d630d6
$ cat ./image/overlay2/layerdb/sha256/da898a2e1b3213abf533c13aed412487af8370de7b77ec31f5334113edcc144b/cache-id
b2a5746a09cee3a4e8af83458fc5e6b292e439c8cc60e89505a013c6ba46956a
$ cat ./image/overlay2/layerdb/sha256/dffdb30cad9ada86a0d504cbb8466ebfbb5fb112338da9a2aaa0b2dba1ee2535/cache-id
ca88b69a3aa5ef096a735c12289d173b1df1406fcd9ac343822d7cfd7fe4bdc7
$ cat ./image/overlay2/layerdb/sha256/b321e8877295f400ca8cc95ca1af92c8c6440e9675a8766ecccc60d81c69fb37/cache-id
550c2aa8fc4074bb49c0938f2c7c40473fe8c036a394439ff9ad6a772911cfb7
$ cat ./image/overlay2/layerdb/sha256/518fdaf2a9e0f3be357d08a342dd39aedbb262f7aa5863ef2f43ceaad17e23b7/cache-id
4272dcce0283c7614e05c0bee3870b3675bb772257e6572462acfa0b7a648a7f
$ cat ./image/overlay2/layerdb/sha256/b741310eed6f050b486dae5427b31da464ef176963a6f85b6a38e1a90ac5323b/cache-id
1ef56f1966660f188b4402d04f0f03efa0dc8974f976d039162db6bdac24ccaa
$ cat ./image/overlay2/layerdb/sha256/8db8f53f4914863a3a8c1a64482dd3ca5e960c3c8d2cf5cd82f81b6c5c32b3a7/cache-id
3ce35d0caaec37c10742f001a15abc0e623f2697906cee223f62ce8b48b0342e

```

```
micahc@tyche /tmp/unpack  $ cat manifest.json  | jq
[
  {
    "Config": "19d027b65340e931103d2e05c1658bf78fd81f3913bb8deacbe1a49b6e98b77f.json",
    "RepoTags": [
      "mdillon/postgis:10-alpine"
    ],
    "Layers": [
      "6f749379d19b0ace9aab81a7ac0abe53f74084bda8f25dbe7795e99499133466/layer.tar",
      "167f732e44357c03c8e8ea994db4451e8e9057d0b4856379fa127129bd81e455/layer.tar",
      "4d91f57cd3540a73bcf63a41ad0a5f8932c2257a97b2a20f43cca879ee72ebf8/layer.tar",
      "04e944734ed89a763d4ae1110f4527167af8baa583655491c9bb5694ac23c1f1/layer.tar",
      "3a882721e2f7fd6b70e63d17cb08f547b9963a2fcde5b67f139c4a64d6efe1e1/layer.tar",
      "df55bef7c463c245fd24b375b9d0083f1da937f3da6060e20d5c9e6a0d996be8/layer.tar",
      "2fe535a6750cbba498c43bb665fd12f18d97e3d5252ae99a796583a705f7f2bc/layer.tar",
      "21dc88f6034c70b0bf2b904a11fad60696263324c8e19970fbbf6af9b9e65b0d/layer.tar",
      "45fe957375aecccdc9902d99ecc17a28940b8d0dfcc065d9f1b4b2c33c309cc8/layer.tar",
      "853ebac8e5df8260e8df5f64ae0af37719a5ba35f0b3a3707a6a4027df55f93d/layer.tar",
      "81cd805fb4f775dd97dc3b6fee85755493bf42755886c0bd93af22a5c1d61e34/layer.tar",
      "50659a5fb576331c2a94226ddb11ab95d5f7b9cc972975458796d15aae34807f/layer.tar"
    ]
  }
]
```

```
[root@tyche docker]# find -name 'lower' | while read line; do echo $line; cat $line; echo ''; done
./overlay2/914c07936ddc76ebc5ccc373dc33a75dd07e7b990f6b67ec56b4ba6ae4d630d6/lower
l/MECBVOSOQ6JJOIO2S23LFIC5MQ:l/UHBZTURYMSPLQUJCWV2KRRSUH5:l/FG4YAC4U7LLUV5OGS3W4TFUUBF:l/SPTVMQM43OTLJEUHZAOQCO75YK:l/LK3UQLPKDWNUNZFLKR6FWGYDCR:l/KSVDNX4576JN3GAH47NPJKLQ4X:l/5VAFOMZUDHZFMSLX2OHRPCWPAJ:l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/847ef282afe912e9b6aab808b477714029e8fbdacaaa39be4d233d54b0ced0b1/lower
l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/ca88b69a3aa5ef096a735c12289d173b1df1406fcd9ac343822d7cfd7fe4bdc7/lower
l/SPTVMQM43OTLJEUHZAOQCO75YK:l/LK3UQLPKDWNUNZFLKR6FWGYDCR:l/KSVDNX4576JN3GAH47NPJKLQ4X:l/5VAFOMZUDHZFMSLX2OHRPCWPAJ:l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/3ce35d0caaec37c10742f001a15abc0e623f2697906cee223f62ce8b48b0342e/lower
l/FG4YAC4U7LLUV5OGS3W4TFUUBF:l/SPTVMQM43OTLJEUHZAOQCO75YK:l/LK3UQLPKDWNUNZFLKR6FWGYDCR:l/KSVDNX4576JN3GAH47NPJKLQ4X:l/5VAFOMZUDHZFMSLX2OHRPCWPAJ:l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/c2a3eb2592736d9e0125bcb53b062a706745d07f1de1647609c1930f87bad8fd/lower
l/KSVDNX4576JN3GAH47NPJKLQ4X:l/5VAFOMZUDHZFMSLX2OHRPCWPAJ:l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/550c2aa8fc4074bb49c0938f2c7c40473fe8c036a394439ff9ad6a772911cfb7/lower
l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/02300b16e0ebe73e9d1cfacf7a7a8d207e222e38f986e0ec6d7f1ee0a9168a4c/lower
l/LK3UQLPKDWNUNZFLKR6FWGYDCR:l/KSVDNX4576JN3GAH47NPJKLQ4X:l/5VAFOMZUDHZFMSLX2OHRPCWPAJ:l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/d486eecbb911812522fc3f071596b529040abd07c3ac15a9cc72cfb46d8e9c38/lower
l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/4272dcce0283c7614e05c0bee3870b3675bb772257e6572462acfa0b7a648a7f/lower
l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/1ef56f1966660f188b4402d04f0f03efa0dc8974f976d039162db6bdac24ccaa/lower
l/UHBZTURYMSPLQUJCWV2KRRSUH5:l/FG4YAC4U7LLUV5OGS3W4TFUUBF:l/SPTVMQM43OTLJEUHZAOQCO75YK:l/LK3UQLPKDWNUNZFLKR6FWGYDCR:l/KSVDNX4576JN3GAH47NPJKLQ4X:l/5VAFOMZUDHZFMSLX2OHRPCWPAJ:l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/b2a5746a09cee3a4e8af83458fc5e6b292e439c8cc60e89505a013c6ba46956a/lower
l/5VAFOMZUDHZFMSLX2OHRPCWPAJ:l/ZQCZ6I2JVCRFXZMXJIVI3DEXAG:l/FMV6VHGQTWBBURR2WWMO733ZAU:l/6TZ45A4GZ4S57N5RJD5ZOSIMWY:l/TMYDVXFVOFFVSEUZSDYMZTJOLU
```

```
[root@tyche docker]# find -name 'link' | while read line; do echo $line; cat $line; echo ''; done
./overlay2/856620bec89104b1554054fe63e4d06aaf953fdc11713a3931f29fcfb794eb29/link
TMYDVXFVOFFVSEUZSDYMZTJOLU
./overlay2/914c07936ddc76ebc5ccc373dc33a75dd07e7b990f6b67ec56b4ba6ae4d630d6/link
6B3RAHVAFPWTGTMDVMFR2J4SK2
./overlay2/847ef282afe912e9b6aab808b477714029e8fbdacaaa39be4d233d54b0ced0b1/link
ZQCZ6I2JVCRFXZMXJIVI3DEXAG
./overlay2/ca88b69a3aa5ef096a735c12289d173b1df1406fcd9ac343822d7cfd7fe4bdc7/link
FG4YAC4U7LLUV5OGS3W4TFUUBF
./overlay2/3ce35d0caaec37c10742f001a15abc0e623f2697906cee223f62ce8b48b0342e/link
UHBZTURYMSPLQUJCWV2KRRSUH5
./overlay2/c2a3eb2592736d9e0125bcb53b062a706745d07f1de1647609c1930f87bad8fd/link
LK3UQLPKDWNUNZFLKR6FWGYDCR
./overlay2/550c2aa8fc4074bb49c0938f2c7c40473fe8c036a394439ff9ad6a772911cfb7/link
FMV6VHGQTWBBURR2WWMO733ZAU
./overlay2/02300b16e0ebe73e9d1cfacf7a7a8d207e222e38f986e0ec6d7f1ee0a9168a4c/link
SPTVMQM43OTLJEUHZAOQCO75YK
./overlay2/d486eecbb911812522fc3f071596b529040abd07c3ac15a9cc72cfb46d8e9c38/link
5VAFOMZUDHZFMSLX2OHRPCWPAJ
./overlay2/4272dcce0283c7614e05c0bee3870b3675bb772257e6572462acfa0b7a648a7f/link
6TZ45A4GZ4S57N5RJD5ZOSIMWY
./overlay2/1ef56f1966660f188b4402d04f0f03efa0dc8974f976d039162db6bdac24ccaa/link
MECBVOSOQ6JJOIO2S23LFIC5MQ
./overlay2/b2a5746a09cee3a4e8af83458fc5e6b292e439c8cc60e89505a013c6ba46956a/link
KSVDNX4576JN3GAH47NPJKLQ4X
```
