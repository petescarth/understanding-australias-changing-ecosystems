import ee



# Function to compute the seasonal median of the collection given a collection and season time
def seasonalMedian(imageCollection,season):
    # Start date of the seasons where the first season is 1
    startDate = ee.Date.fromYMD(1988,1,1).advance(3 * (season - 1),'month');
    # Seasonal Increment - 3 months from the starting date
    endDate = startDate.advance(3,'month');
    # Double Check the Logic
    # print "%s Days" % ((endDate.getInfo()['value']-startDate.getInfo()['value'])/(1000*3600*24))
    # Select the TOA-adjusted L1T scenes
    landsatCollection = ee.ImageCollection(imageCollection).filterDate(startDate, endDate);
    # create an image from the collection
    return landsatCollection.median()

# Function to rescale the image to RSC TOA and compute the image transforms
# TODO: Recompute algorithm based on EE percentile composite calibration to remove operation count below
def applyRSCtransforms(toaImage):
    # Select the algorithm bands and rescale to Qld RSC values
    gains = ee.Image([325.0, 345.0, 290.0, 425.0, 275.0]);
    offsets = ee.Image([1, 1, 6, 6, 6]);
    useBands = toaImage.select("20", "30", "40", "50","70").multiply(gains).add(offsets).divide(256);
    logBands = useBands.log();
    # Combine the bands into a new image
    return ee.Image.cat(
      useBands.expression("b('20') * b('30')"),
      useBands.expression("b('20') * b('40')"),
      useBands.expression("b('20') * b('50')"),
      useBands.expression("b('20') * b('70')"),
      useBands.expression("b('20') * logs", {'logs': logBands}),
      useBands.expression("b('30') * b('40')"),
      useBands.expression("b('30') * b('50')"),
      useBands.expression("b('30') * b('70')"),
      useBands.expression("b('30') * logs", {'logs': logBands}),
      useBands.expression("b('40') * b('50')"),
      useBands.expression("b('40') * b('70')"),
      useBands.expression("b('40') * logs", {'logs': logBands}),
      useBands.expression("b('50') * b('70')"),
      useBands.expression("b('50') * logs", {'logs': logBands}),
      useBands.expression("b('70') * logs", {'logs': logBands}),
      logBands.expression("b('20') * b('30')"),
      logBands.expression("b('20') * b('40')"),
      logBands.expression("b('20') * b('50')"),
      logBands.expression("b('20') * b('70')"),
      logBands.expression("b('30') * b('40')"),
      logBands.expression("b('30') * b('50')"),
      logBands.expression("b('30') * b('70')"),
      logBands.expression("b('40') * b('50')"),
      logBands.expression("b('40') * b('70')"),
      logBands.expression("b('50') * b('70')"),
      useBands,
      logBands,
      ee.Image(1.3))


# Helper Class to display 2 images side by side
# Nice for checking processing
class sideBySide():
    def __init__(self, *frames):
        self.frames = frames
    def _repr_html_(self):
        width = 100. / len(self.frames)
        s = ""
        for f in self.frames:
            s += "<div style='float: left;'>%s</div>" % f._repr_html_()
        return s


# A progress bar class used like this:
# p = ProgressBar(1000)
# for i in range(1001):
#    p.animate(i)

class progressBar:
    def __init__(self, iterations):
        self.iterations = iterations
        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 40
        self.__update_amount(0)
        self.animate = self.animate_ipython

    def animate_ipython(self, iter):
        print '\r', self,
        self.update_iteration(iter + 1)

    def update_iteration(self, elapsed_iter):
        self.__update_amount((elapsed_iter / float(self.iterations)) * 100.0)
        self.prog_bar += '  %d of %s complete' % (elapsed_iter, self.iterations)

    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) // 2) - len(str(percent_done))
        pct_string = '%d%%' % percent_done
        self.prog_bar = self.prog_bar[0:pct_place] + \
            (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)



# Function to initialise the EE using a service account and key
def startEE():
  serviceAccount = '252101174119@developer.gserviceaccount.com'
  keyLocation = '../../.key'
  ee.Initialize(ee.ServiceAccountCredentials(serviceAccount,keyLocation))
  print "Initialized EE"

