import mcs

from mcs.data_loaders import sniffer


loader = sniffer.SNIFFERdataloader()
df = loader.load_data('snifferdata')
df.shape
df.head(10)