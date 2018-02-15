import os, re, glob, csv, xlrd, json, ast, argparse, sys, shutil
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

sheetRoot = '/space/jazz/1/users/gwarner/histograms/'
setup = SetUp(sheetRoot)
setup.handle_inputs()
sheets = setup.getSpreadSheets()

histData = OrganizeHistogramData(vendors=setup.vendors, maps=setup.maps, filetype=setup.sheetType, spread=sheets)
