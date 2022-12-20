{
  description = "Monti (remote monitoring system) backend restful API";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        customPython = (pkgs.python310.withPackages(ps : with ps; [
            flask
            ipython
            pandas
            qrcode
            matplotlib
            sphinx
            sphinx_rtd_theme
            pytest
            pytest-mock
            pytest-flask
            waitress
          ]));
      in
        rec {
          devShells.default = pkgs.mkShell {
            PYTHONPATH = "${self}/src";
            buildInputs = with pkgs; [
              customPython
              git
            ];
          };
        }
      );
}
