# vnpy_chart

enhanced chart for vnpy

## tips

### numpy

use the last version of 1.x:

```sh
pip install numpy==1.26.4 
```

### ta-lib

If you encounter issues while installing [ta-lib](https://github.com/TA-Lib/ta-lib-python), try [talib-build](https://github.com/cgohlke/talib-build/releases):

```sh
wget https://github.com/cgohlke/talib-build/releases/download/v0.4.32/TA_Lib-0.4.32-cp312-cp312-win_amd64.whl -O TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
pip install TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
```

## dev

### run test

```sh
pip install .
python -m unittest discover -s tests
```

### publish

1. install tools

```sh
pip install --upgrade importlib_metadata build twine
```

2. build

```sh
python -m build
```

3. upload to testpypi

```sh
python -m twine upload --repository testpypi dist/*
```

4. upload to pypi

```sh
python -m twine upload dist/*
```
