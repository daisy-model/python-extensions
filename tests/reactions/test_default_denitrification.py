'''
Test daisy_extensions.reactions.default_nitrification
See test-data/default-denitrification.dai for example dai file using the module
'''
from pathlib import Path
import pandas as pd
from daisypy.io import read_dlf
from daisy_extensions.reactions.default_denitrification import (
    default_denitrification, plf, pressure_response
)
from ..markers import requires_daisy
from ..helpers import run_daisy

def test_pressure_response():
    '''Ensure that we fo through all the branches'''
    assert pressure_response(10) == 0.6
    assert pressure_response(0) == 0.6
    assert pressure_response(-1) == 0.6
    assert pressure_response(-10) == 0.6 + 0.4 * 1 / 1.5
    assert pressure_response(-100) == 1
    assert pressure_response(-1000) == 1 - (3 - 2.5) / (6.5 - 2.5)
    assert pressure_response(-1e7) == 0

def test_plf():
    '''Ensure that we fo through all the branches'''
    x = [0, 0.5, 1]
    y = [-1, 1, -1]
    assert plf(x, y, -1) == -1
    assert plf(x, y, 0) == -1
    assert plf(x, y, 0.25) == 0
    assert plf(x, y, 0.5) == 1
    assert plf(x, y, 0.75) == 0
    assert plf(x, y, 1) == -1
    assert plf(x, y, 2) == -1

def test_python():
    '''Compare with previously computed outputs'''
    data_dir = Path(__file__).parent / 'test-data'
    df = pd.read_csv(data_dir / 'default-denitrification-args-and-targets.csv')
    targets = ['N2O-deni', 'N2-deni']
    for _, row in df.iterrows():
        args = { k:v for k,v in row.items() if k not in targets }
        expected = { k:v for k,v in row.items() if k in targets }
        result = default_denitrification(**args)
        for k,v in expected:
            assert v == result[k]

@requires_daisy
def test_daisy(tmp_path):
    '''Compare with previously computed dlf file'''
    data_dir = Path(__file__).parent / 'test-data'
    dai_file = data_dir / 'default-denitrification.dai'
    assert run_daisy(tmp_path, dai_file).returncode == 0
    dlf = read_dlf(tmp_path / 'soil_python.dlf')
    expected = pd.read_csv(data_dir / 'expected-default-denitrification.csv')
    assert expected.equals(dlf.body)
