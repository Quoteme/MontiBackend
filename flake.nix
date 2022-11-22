{
  description = "Monti (remote monitoring system) backend restful API";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils = {
      inputs.nixpkgs.follows = "nixpkgs";
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
          ]));
      in
        rec {
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              customPython
              git
            ];
          };
        }
      );
}
