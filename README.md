# vnpy_chart

enhanced chart for vnpy

## tips

If you encounter issues while installing [ta-lib](https://github.com/TA-Lib/ta-lib-python), try:

```sh
pip install numpy==1.26.4 importlib_metadata
pip install --extra-index-url https://pypi.vnpy.com TA_Lib==0.4.24
```

## dev

```sh
pip install .
python -m unittest discover -s tests
```
