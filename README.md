# Sort-Exif
Image/Movie file sorter using Exiftool  
Copy image/movie files recursively sorting by EXIF:DateTimeOriginal  
If EXIF:DateTimeOriginal isn't available use other oldest date instead.  

## Dependencies
- Exiftool ( https://smarnach.github.io/pyexiftool/ )  

## Usage
```
$ python sort-exif.py <source_dir> <dest_dir>
```
### example
```
$ python sort-exif.py photos_from photos_to
```
