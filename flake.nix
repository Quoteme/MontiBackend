{
  description = "Monti (remote monitoring system) backend restful API";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
    pypi-deps-db = {
      url = "github:DavHau/pypi-deps-db";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.mach-nix.follows = "mach-nix";
    };
    mach-nix = {
      url = "github:DavHau/mach-nix/3.5.0";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
      inputs.pypi-deps-db.follows = "pypi-deps-db";
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
          ]));
      in
        rec {
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              customPython
              git
            ];
          };
          devShells.documentation = pkgs.mkShell {
            buildInputs = with pkgs; [
              # See: https://github.com/Quoteme/mach-nix-template
              ( inputs.mach-nix.lib.${system}.mkPython {
                python = "python310";
                requirements = ''
                  # Sphinx
                  # sphinx-rtd-theme
                  # sphinx-autodoc-annotation
                '';
              })
            ];
          };
        }
      );
}
