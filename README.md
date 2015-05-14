# microscopestitching

[![build-status-image]][travis]
[![pypi-version]][pypi]
[![wheel]][pypi]

## Overview

This software aims to be a reliable way to stitch your microscope images. To
get good results, a couple of assumptions should be true about your dataset:

- images are regular spaced
- images are of same size
- side by side images have translation only in one dimension
  - (if not, check your scanning mirror rotation)
- scale in edge of images are constant

## Installation

Install using `pip`...

```bash
pip install microscopestitching
```

## Example
```python
from microscopestitching import stitch
from skimage.io import imsave

images = []
for i in range(50):
    row = i // 10
    col = i % 10
    images.append(('%d.png' % i, row, col))

merged = stitch(images)
imsave('merged.png', merged)
```

See also [notebook examples](http://nbviewer.ipython.org/github/arve0/microscopestitching/blob/master/notebooks/).

## API reference

API reference is at http://microscopestitching.rtfd.org.

## Development
Install dependencies and link development version of microscopestitching to pip:
```bash
git clone https://github.com/arve0/microscopestitching
cd microscopestitching
pip install -r requirements.txt # install dependencies and microscopestitching-package
```

### Testing
```bash
tox
```

### Build documentation locally
To build the documentation:
```bash
pip install -r docs/requirements.txt
make docs
```



[build-status-image]: https://secure.travis-ci.org/arve0/microscopestitching.png?branch=master
[travis]: http://travis-ci.org/arve0/microscopestitching?branch=master
[pypi-version]: https://pypip.in/version/microscopestitching/badge.svg
[pypi]: https://pypi.python.org/pypi/microscopestitching
[wheel]: https://pypip.in/wheel/microscopestitching/badge.svg
