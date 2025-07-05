# shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python312.withPackages(ps: with ps; [
      uv
    ]))
    poetry
    git
    libmediainfo
    ffmpeg
  ];

  shellHook = ''
    # optionally activate a virtualenv here
  '';
}

