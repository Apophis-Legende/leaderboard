
{ pkgs }: {
  deps = [
    pkgs.zlib
    pkgs.tk
    pkgs.tcl
    pkgs.openjpeg
    pkgs.libxcrypt
    pkgs.libwebp
    pkgs.libtiff
    pkgs.libjpeg
    pkgs.libimagequant
    pkgs.lcms2
    pkgs.freetype
    pkgs.geckodriver
    pkgs.chromium
  ];
  env = {
    CHROME_BIN = "${pkgs.chromium}/bin/chromium";
  };
}
