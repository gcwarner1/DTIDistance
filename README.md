Basic Usage Pipeline

1.) Retrieve radiology reports from RPDR

2.) Once you have retrieved your radiology reports for the RPDR database you need to filter out the ones with any physiological abnormalities or that don't contain diffusion data and compile a list of the medical record numbers (MRNs) associated to the files deemed relevant to the study. This can be accomplished by using the FindHealthyDti() module in GetData/filterHealthyDtiFromRadiologyReports.py.

3.) Retrieve data associated with MRNs isolated in step two from Mi2b2.

4.) Delete all non diffusion data returned from Mi2b2. Convert remaining data to nifti format, delete corrupted data, process, and generated thresholded FA/MD maps. This can be accomplished using the DataSet() module in ProcessDtiData/processDtiData.py which uses DiffRecon_Rotate_B_Matrix.sh and fdt_rotate_bvecs.sh

5.) If making a histogram involving two or more independent variables (i.e. all GE data with 30 gradient directions and a 1.5T static field strength) edit and run CalculateDistances/specific_hist_dist_csv.py. If you are making a histogram involving a single independent variable (i.e. all data with a b-value of 1000) edit and run CalculateDistances/hist_dist_between_csv.py.

6.) Generate histogram plot and bin histogram values in text file for comparison. Do this by editing and runing MakeHistograms/makeCsv.py. Check the data at the far tail of the distribution to isolate any 

7.) Make plots. To make box and whisker plots edit and run PlottingScripts/make_box_plots.py. To make simple histogram representation of the FA/MD distribution of a single map edit and run PlottingScripts/makeBasicPlot.py. To make cumulative frequency histograms and obtain the Kolmogorov-Smirnov test statistic edit and run PlottingScripts/make_cumulative_Kolmogrov_plot.py


This code has been heavily refactored in order to make it more useful to other researchers. The original code that was actually used to perform the analysis in the "Characterization of Diffusion Metric Map Similarity in Data from a Clinical PACS using the Histogram Distance" paper can be found in the "legacy_code" directory.
