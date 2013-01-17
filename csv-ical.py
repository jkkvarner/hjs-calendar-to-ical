import csv, codecs, cStringIO, os, re, sys, datetime
from optparse import OptionParser

debug = False

class TextRecoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.encoding = encoding
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode(self.encoding)
#        return self.reader.next().encode("utf-8")

class TextCSVReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="windows-1250", delimiter=';', quotechar='|', **kwds):
        self.encoding = encoding
        self.f = TextRecoder(f, encoding)
        self.reader = csv.reader(self.f, dialect=dialect, delimiter=delimiter, quotechar=quotechar, **kwds)

    def next(self):
        row = self.reader.next()
        return [s.decode("windows-1250") for s in row]

    def __iter__(self):
        return self

def dateFormat(year, date, dateCorrection = 0):
    if debug:
        print date
    arr = date.partition('.')
    if debug:
        print arr[2]
    month = int(arr[2].replace('.', ''))
    day = int(arr[0])

    datum = datetime.date(int(year), month, day) + datetime.timedelta(days=dateCorrection)
    return str(datum.year) + intFormat(datum.month) + intFormat(datum.day)

def intFormat(i):
    fill = ''
    if i < 10:
        fill = '0'
    return str(fill) + str(i)

def checkExport(optionsKlase, klase):
	k = re.split('\W+', optionsKlase)
	for klasa in k:
		if re.match(klasa, klase, re.IGNORECASE):
			return True
	return False

parser = OptionParser()
parser.add_option("-k", "--klase", dest="klase", help="Klase")

(options, args) = parser.parse_args()

f = args[0]
fileName, fileExtension = os.path.splitext(os.path.basename(f))
dirName = os.path.dirname(f)

iCalFile=dirName + '/' + fileName
if options.klase:
	iCalFile=iCalFile + "-" +  options.klase
iCalFile=iCalFile + '.ical'
print iCalFile

m = re.search('(\d\d\d\d)', fileName)
if m:
    year = m.group(0)
else:
    now = datetime.datetime.now()
    year = now.year

with open(iCalFile, 'w') as outFile:
    outFile.write('BEGIN:VCALENDAR\r\n')
    outFile.write('PRODID:-//Google Inc//Google Calendar 70.9054//EN\r\n')
    outFile.write('VERSION:2.0\r\n')
    outFile.write('CALSCALE:GREGORIAN\r\n')
    outFile.write('METHOD:PUBLISH\r\n')
    outFile.write('X-WR-CALNAME:JK Kvarner\r\n')
    outFile.write('X-WR-TIMEZONE:Europe/Belgrade\r\n')
    outFile.write('X-WR-CALDESC:\r\n')

    firstRow = True
    with open(f, 'rb') as inFile:
        reader = TextCSVReader(inFile)
        for row in reader:
            if firstRow:
                firstRow = False
                continue
            if not row[1]:
                if debug:
                    print 'Skipping empty row!'
                continue
            if debug:
                print '---------------------------------------------------------------'
                print row
                print row[0]

            try:
            	dateFrom = dateFormat(year, row[1])
            	dateTo = dateFormat(year, row[2], 1)
            except :
                print ('WARNING: Skipping invalid event! %s' % row)
                continue

            regata = row[3]
            organizator = row[4]
            mjesto = row[5]
            klase = row[6]
            kategorija = row[7]
            if options.klase and not checkExport(options.klase, klase):
            	    continue
            
            outFile.write('BEGIN:VEVENT\r\n')
            outFile.write('DTSTART;VALUE=DATE:%s\r\n' % dateFrom)
            outFile.write('DTEND;VALUE=DATE:%s\r\n' % dateTo)
            outFile.write('DESCRIPTION:%s, Klase: %s, Kategorija: %s\r\n' % (regata.encode("utf-8"), klase.encode("utf-8"), kategorija.encode("utf-8")))
            outFile.write('LOCATION:%s, %s\r\n' % (organizator.encode("utf-8"), mjesto.encode("utf-8")))
            outFile.write('SEQUENCE:0\r\n')
            outFile.write('STATUS:CONFIRMED\r\n')
            outFile.write('SUMMARY:%s, %s\r\n' % (regata.encode("utf-8"), organizator.encode("utf-8")))
            outFile.write('TRANSP:TRANSPARENT\r\n')
            outFile.write('END:VEVENT\r\n')
            if debug:
                print '/--------------------------------------------------------------'

    outFile.write('END:VCALENDAR\r\n')
