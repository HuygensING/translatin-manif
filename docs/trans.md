## Transporting and transforming data

Some steps (those between **begin 🆔** - **end 🆔**)  can only be executed
within the KNAW/HuC network, other steps can be followed by everyone.

It all starts with cloning this repo,
[translatin/corpus](https://gitlab.huc.knaw.nl/translatin/corpus),
to your own computer:

```
mkdir -p ~/gitlab.huc.knaw.nl/translatin
cd ~/gitlab.huc.knaw.nl/translatin
git clone http://gitlab.huc.knaw.nl/translatin/corpus.git
```

**begin 🆔**

The next step is to drag in the source data from the internal fileshare.

This starts with cloning the internal
[tt/translatin](https://code.huc.knaw.nl/tt/translatin)
repo to your computer.

```
mkdir -p ~/code.huc.knaw.nl/tt
cd ~/code.huc.knaw.nl/tt
git clone http://code.huc.knaw.nl/tt/translatin.git
cd translatin
```

In the file `source.yaml` you see the machine where the source data is.
Ensure you have a login on that machine and that you can `ssh` into it.

Now you can use the script `get.sh` to get the source data:

```
cd ~/code.huc.knaw.nl/tt/translatin
./get.sh dirkr
```

(instead of dirkr pass your own user name on the remote machine).

You see the material pop up in 

```
~/gitlab.huc.knaw.nl/translatin/corpus/local
```

**end 🆔**

Now you are in the open again.
The next step is to *organize* the source data into a directory structure
with nice and short file names, and to compile yaml files with metadata of
the manifestations out of various parts of the source data.
From the programs directory in the public repo do: 

```
cd ~/gitlab.huc.knaw.nl/translatin/corpus/programs
./make.sh organize
```

You could also break this up into two steps:

```
./make.sh meta
./make.sh data
```

**begin 🆔**

It is a good idea to put this organized data back to the source, into a separate
directory there. Then other people can get it from there without the hassle of
running the somewhat intricate `make` script for this. You put the data back by 
saying:

```
cd ~/code.huc.knaw.nl/tt/translatin
./putback.sh dirkr
```

If, later on, you or somebody else wants to retrieve this organized data,
that can be done by

```
cd ~/code.huc.knaw.nl/tt/translatin
./getorganized.sh dirkr
```

You see the material pop-up in

```
~/gitlab.huc.knaw.nl/translatin/corpus/organized
~/gitlab.huc.knaw.nl/translatin/corpus/meta
```

**end 🆔**

Back in the open, you have access to all data:

*   the source data in `local`
*   the organized data in `organized`
*   the produced text-fabric data in `tf`
*   the produced Text/AnnoRepo data in `watm`

You can also regenerate the TF and WATM data by means of the same `make.sh` script:

```
cd ~/gitlab.huc.knaw.nl/translatin/corpus/programs
./make.sh produce
```

or, in separate steps:

```
./make.sh tf
./make.sh watm
```
