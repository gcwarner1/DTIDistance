1.) Retrieve radiology reports from RPDR

2.) Once you have retrieved your radiology reports for the RPDR database you need to filter out the ones with any physiological abnormalities or that don't contain diffusion data and compile a list of the medical record numbers (MRNs) associated to the files deemed relevant to the study. This can be accomplished by using the FindHealthyDti() module in thefilterHealthyDtiFromRadiologyReports.py file.

3.) Retrieve data associated with MRNs isolated in step two from Mi2b2.

4.) Delete all non diffusion data returned from Mi2b2. Convert remaining data to nifti format, delete corrupted data, process, and generated thresholded FA/MD maps. This can be accomplished using the DataSet() module of the processDtiData.py file which uses DiffRecon_Rotate_B_Matrix.sh and fdt_rotate_bvecs.sh

5.)
