
import logging
from RebotConfig import RebotConfig
#

logging.basicConfig(filename='%s%s' % (RebotConfig.path, RebotConfig.log), level=logging.INFO, filemode='a+')
class Log():

    @staticmethod
    def d(content):
        #f = open('%s%s' % (RebotConfig.path, RebotConfig.log), 'a+');
        #f.write('%s\n' % content)
        #f.close();
        print content;
        logging.info(content)
        #print content;
