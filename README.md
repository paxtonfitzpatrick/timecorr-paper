# What is the neural code?

This repository contains data and code used to produce the paper [_High-level cognition during story listening is reflected in high-order dynamic correlations in neural activity patterns_](https://doi.org/10.1101/763821) by Lucy L.W. Owen, Thomas H. Chang, and Jeremy R. Manning.  You may also be interested in our [timecorr](https://timecorr.readthedocs.io/en/latest/) Python toolbox for calculating high-order dynamic correlations in timeseries data; the methods implemented in our timecorr toolbox feature prominently in our paper.

This repository is organized as follows:

```
root
└── code : all code used in the paper
    ├── notebooks : jupyter notebooks for paper analyses and instructions for downloading the data
    └── scripts : python scripts used to run analyses on a computing cluster
    └── figs : pdf and png copies of figures
└── data : create this folder by extracting the following zip archive into your clone of this repository's folder: https://drive.google.com/file/d/1CZYe8eyAkZFuLqfwwlKoeijgkjdW6vFs
└── paper : all files to generate paper
    └── figs : pdf copies of each figure
```

Content of the data folder is provided [here](https://drive.google.com/file/d/1CZYe8eyAkZFuLqfwwlKoeijgkjdW6vFs/view?usp=sharing).
We also include a Dockerfile to reproduce our computational environment. Instruction for use are below:

## Conda env setup
1.


## Docker setup
1. Install Docker on your computer using the appropriate guide below:
    - [OSX](https://docs.docker.com/docker-for-mac/install/#download-docker-for-mac)
    - [Windows](https://docs.docker.com/docker-for-windows/install/)
    - [Ubuntu](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
    - [Debian](https://docs.docker.com/engine/installation/linux/docker-ce/debian/)
2. Launch Docker and adjust the preferences to allocate sufficient resources (e.g. > 4GB RAM)
3. Build the docker image by opening a terminal in this repo folder and enter `docker build -t timecorr_paper .`  
4. Use the image to create a new container
    - The command below will create a new container that will map your local copy of the repository to `/mnt` within the container, so that location is shared between your host OS and the container. The command will also share port `9999` with your host computer so any jupyter notebooks launched from *within* the container will be accessible in your web browser.
    - `docker run -it -p 9999:9999 --name Timecorr_paper -v $PWD:/mnt timecorr_paper `
    - You should now see the `root@` prefix in your terminal, if so you've successfully created a container and are running a shell from *inside*!
5. To launch any of the notebooks: `jupyter notebook`

## Using the container after setup
1. You can always fire up the container by typing the following into a terminal
    - `docker start --attach Timecorr_paper`
    - When you see the `root@` prefix, you're inside the container
2. Stop a running jupyter notebook server with `ctrl + c`
3. Close a running container with `ctrl + d` or `exit` from the same terminal window you used to launch the container, or `docker stop Timecorr_paper` from any other terminal window
