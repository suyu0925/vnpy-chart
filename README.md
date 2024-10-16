# vnpy_chart

enhanced chart for vnpy

## tips

If you encounter issues while installing [ta-lib](https://github.com/TA-Lib/ta-lib-python), try:

```sh
pip install numpy==1.26.4 importlib_metadata
pip install --extra-index-url https://pypi.vnpy.com TA_Lib==0.4.24
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
pip install --upgrade build twine
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
