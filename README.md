# MUR
Tool written in Python to download comics from Marvel Unlimited.

**Originally forked from [Sorrow446](https://github.com/Sorrow446/MUR)**

**People have been seen selling my tools; DO NOT buy them. My tools are free and always will be.**

# Features
- Lossless exporting to CBZ or PDF.
*Comics are provided by MARVEL as JPGs. MUR doesn't apply any compression whatsoever.
- Multi-URL and whole series input support via CLI.
- Write comic metadata to JSON file.
- Multi-platform support.
- F-string-free; may also work on Python 2.

# Setup
**A subscripton is required to use MUR:**
1. Login to [Marvel](http://www.marvel.com/).
2. Install the "cookies.txt" extension for [chrome](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en) or [firefox](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en).
3. Save cookies to txt file (current tab only).
4. Move "cookies.txt" to MUR's directory.


**To download an entire series at a time, a Marvel developer account is needed:**
1. Login to [Marvel](http://www.marvel.com/)
2. Sign up for a [developer account](https://developer.marvel.com/account)
3. Save your public and private keys on your Marvel developer account page
    - These can be either be passed in as arguments, or saved to a keys.txt file in MUR's home directory
    - Format for keys.txt:
        ```
        private key
        public key
        ```
Your cookies may become unusable after a long while; just repeat the dumping process.

# Usage
MUR may only be used via CLI.

Download a single comic and export to PDF:
```
mur.py -u https://www.marvel.com/comics/issue/67930/captain_america_2018_12 -f pdf
```

Download two comics, export to CBZ and write comic's metadata to JSON file:
```
mur.py -u https://www.marvel.com/comics/issue/... https://www.marvel.com/comics/issue/... -f cbz -m
```

Download an entires series and save as CBZ
```
mur.py -u https://www.marvel.com/comics/series/24503/captain_america_2018_-_present -f cbz
```


**Full usage:**
```
usage: mur.py [-h] -u [URL [URL ...]] -f {cbz,pdf} [-m]

Sorrow446.

optional arguments:
  -u [URL [URL ...]]        --url [URL [URL ...]]
                                URL - www.marvel.com/comics/issue/# (for one issue) or
                                read.marvel.com/#/book/ (for one issue) or
                                www.marvel.com/comics/series/# (for entire series)
  -f {cbz,pdf}, --format    {cbz,pdf}
                                Export format.
  -m, --meta                Write comic's metadata to JSON file.
  --pub [PUBLIC KEY]        Your Marvel devleoper public key
                                If not saved to keys.txt, this is required to download entire series
  --priv [PRIVATE KEY]      Your Marvel developer private key
                                If not saved to keys.txt, this is required to download entire series
  -h, --help                show this help message and exit
```
Accepted URL formats:
```
# For one issue:
1. https://www.marvel.com/comics/issue/<id>/...
2. https://read.marvel.com/#/book/<id>

# For entire series
3. www.marvel.com/comics/series/#
```

# Disclaimer
- I will not be responsible for how you use MUR.
- MARVEL brand and name is the registered trademark of its respective owner.
- MUR has no partnership, sponsorship or endorsement with MARVEL.
