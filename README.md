# Python InterfaceLIFT Downloader
A Python script to download wallpapers from [interfacelift.com](https://interfacelift.com/). This script has multithreading support.

## Usage

```
$ python interfacelift-downloader.py [-d DEST] [-t THREADS] [resolution]
```

If not specified, the default parameters used are:

- **Resolution:** 1920x1080
- **Destination Directory:** ./wallpapers
- **Threads:** 4

To list available resolutions:

```
$ python interfacelift-downloader.py --list
```

### Examples

To download `1920x1080` wallpapers to the `./wallpapers` directory

```
$ python interfacelift-downloader.py 1920x1080
```

To download `1600x900` wallpapers using `8` threads

```
$ python interfacelift-downloader.py -t 8 1600x900
```

To download `1600x900` wallpapers to the `./wallpapers/1600x900` directory

```
$ python interfacelift-downloader.py -d "wallpapers/1600x900" 1600x900
```

# License

This script is licensed under the terms of the MIT license.
