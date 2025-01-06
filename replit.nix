
{ pkgs }: {
  deps = [
    pkgs.geckodriver
    pkgs.chromium
  ];
  env = {
    CHROME_BIN = "${pkgs.chromium}/bin/chromium";
  };
}
