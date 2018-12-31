# Spectron3000

### Dash application for viewing astronomical spectra

Spectron3000 is a web app written in Python using Dash/Flask as the
web framework. Functionality in this app is simple: the user can load
in astronomical spectra, and overlay catalogs of molecules to perform
rudimentary assignments.

In its current form, Spectron3000 is quite restrictive in terms of the
data input. Spectra should be supplied with tab-delimiting, with frequency
in MHz and intensities in Jy/beam. Reference spectra must be in the SPCAT
format.

### What it does

Spectron3000 uses Plotly to render spectra in your web browser. Catalog
frequencies and intensities are used to simulate what the expected flux
of each molecule is based on a hypothetical column density and temperature.
Each line is convolved with a Gaussian lineshape corresponding to a user
supplied value for the Doppler shift.

### How to run Spectron3000

In this folder, there is a shell script named `startSpectron.sh`. In a
terminal window on Linux, simply navigating to this folder and typing
`./startSpectron.sh` should be suffice to start the web app server.

You will need to open your preferred web browser, and use the URL:

http://localhost:8050

### How to use Spectron3000

Operation of Spectron3000 should be relatively straight forward. You
can drag and drop files into the upload form, which will get processed
by the wizard behind the curtain. Note that the program relies on file
extensions to recognize the difference between spectra and catalog files:
spectra can have `.txt, .csv, .spec` as extensions, while catalogs can
have `.lin, .cat`. Multiple files can be uploaded simultaneously.

Once you have a spectrum loaded up, it will be plot in the main graph
area. You can use various tools (e.g. zoom, pan, hover, snapshot) supplied
by Plotly in the top right area of the graph, and use the mouse to navigate
the plot.

Once a spectrum is supplied, the user can provide several catalog files.
The catalog files are loaded in, and synthetic spectra are created for each
molecule. The parameters used to generate the synthetic spectra are shown
and can be modified in the `DataTable` at the bottom of the page. Each time
a new file is uploaded or the parameters are changed, the plot should
upload itself. Depending on the data set, this may take a few seconds and
so please be patient.

---

## TODO

- More file types and more intelligent parsing of spectra/catalogs
- Export DataTable entries as a csv and/or LaTeX table
- Improve performance in the plot updating - must be some Dash backend
optimization that can be done to make it quicker.
