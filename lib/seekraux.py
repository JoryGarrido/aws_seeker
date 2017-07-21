import sys
import time
import itertools

#######################################################################
						#Helper Functions#
#######################################################################

username = ""
password = ""
recepient = ""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Find Between finds a string between two substrings
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
    	print "error"
        return ""
done = False
#Animation Function
def animate():
	spinner = itertools.cycle(['-', '\\', '|', '/'])
	while not done:
		sys.stdout.write(spinner.next())  # write the next character
		time.sleep(0.2)
		sys.stdout.flush()                # flush stdout buffer (actual character display)
		sys.stdout.write('\b')            # erase the last written char

#Check for Services
def service_check(curl_output):
	if "8080" in curl_output:
		#print "............. Port 8080"
		return

#Send email via google
def send_warning(profile, subject, warning):
	SERVER = "smtp.gmail.com:465"
	FROM = "sec_check@{}".format(os.uname()[1])
	TO = ["{}".format(recepient)]

	SUBJECT = "ALERT: Misconfiguration on {}".format(profile)

	TEXT =\
	"""Warning: 

	The following security groups were identified as being publicly accessible during a scan:
	{}\n
	--------------------------------------------------------------------
	This message was generated by sec_check.py, a tool by Thomas Wilson,
	used to identify security failings in local environments.""".format(warning)

	message = "Subject: {}\n\n{}".format(SUBJECT, TEXT)


	server = smtplib.SMTP_SSL(SERVER)
	server.ehlo()
	server.login(username, password)
	server.sendmail(FROM, TO, message)
	server.quit()