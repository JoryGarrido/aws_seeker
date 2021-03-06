import nmap

#######################################################################
							#Perform NMAP#
#######################################################################
#Function for nmap to scan for opened ports, determine exposure and need for sslscan
def perform_nmap(host_ip, nm):

	#Initialize hostname from nmap instance
	host_name_address = nm['{}'.format(host_ip)].hostname()
	#Identify all protocols detected

	#Set need for ssl scan to false by default
	ssl_scan_needed = False

	#Output logging information
	print('Host :  ({} : {})'.format( host_ip, host_name_address))
	print('State : {}'.format(nm['{}'.format(host_ip)].state()))
		
	for proto in nm['{}'.format(host_ip)].all_protocols():

		#Output logging information
		print('----------')
		print('Protocol : {}'.format(proto))
		
		#Identify and sort ports
		lport = nm[host_ip][proto].keys()
		lport.sort()

		for port in lport:
			#If HTTP or HTTPS traffic is accepted, mandate ssllabs-scan
			if port == 80 or port == 443:
				ssl_scan_needed = True
			print('port : {}\tstate : {}'.format(port, nm[host_ip][proto][port]['state']))
	return host_name_address, ssl_scan_needed

#######################################################################
						#Perform SSL Labs Scan#
#######################################################################
#Function to execute ssllabs-scan, reporting in a reduced format. Primarily focused on the grade. Recurses once if the Hostname mismatches the CNAME
#and tries again with the CNAME. Otherwise the scan accepts the failure.
def perform_ssllabs_scan(host_name_address, recursed):

	
	if not os.path.exists('{}/Experiments/ssllabs-scan/ssllabs-scan'.format(os.environ['HOME'])):
		return "The program ssllabs-scan not installed on this system."

	#Open ssllabs-scan from relative path. Ignore mismatches with SSL certificates (we will handle that here)
	ssl_output = subprocess.Popen(['{}/Experiments/ssllabs-scan/ssllabs-scan'.format(os.environ['HOME']), '--ignore-mismatch', '{}'.format(host_name_address)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	
	
	#Initialize local variables.
	criteria = ["\"protocol\"", "grade", "hasWarnings", "vulnBeast", "stsStatus", "supportsRc4", "rc4WithModern","rc4Only", "heartbleed","heartbeat","poodle","fallback","freak","statusMessage"]
	ssllabs_scan_result = ""
	common_flag = False
	mismatch = False

	#Output logging information.
	if recursed == False:
		print('----------')
		print('SSL Labs Evaluaion:')
	
	for line in ssl_output.stdout:
		#Print the criteria we are looking for, and only that criteria.
		if any(c in line for c in criteria):
			ssllabs_scan_result += "{}\n".format(line.rstrip())
		#If we have the common name, grab it here.
		if common_flag == True and recursed == False:
			common_name = line
			common_flag = False
		#Must be set after the check for common_flag. Next line will contain the common name.
		if "commonNames"  in line and recursed == False:
			common_flag = True
		#Trust issue identified, mismatch set.
		if "\"grade\": \"T\"" in line:
			mismatch = True

	#Parse the common name from the JSON object.
	if (mismatch == True and recursed == False):
		common_name = common_name.split("\"")[1]
	#If there was a mismatch, retry with CNAME from certificate, unless this was already tried once.
	if mismatch == True and recursed == False :
		print("...certificate mismatch, trying CNAME")
		ssllabs_scan_result = perform_ssllabs_scan(common_name, True)

	#Pass up string containing results.
	return ssllabs_scan_result


#######################################################################
#######################################################################
							#Extended Scan#
#######################################################################
#######################################################################
def extended_scan(public_ips):

	
	port_arg = """-p 1-1024,1200,1234,1434,1471,1604,1723,1900,1911,1962,2067,
	2082,2083,2086,2087,2123,2152,2323,2375,2376,2404,2455,2628,3000,3128,3306,
	3386,3388,3389,3479,3780,3790,4022,4040,4369,4443,4500,4911,4949,5000,5001,
	5006,5007,5008,5060,5094,5222,5353,5357,5432,5560,5632,5900,5901,5985,5986,
	6000,6379,6666,7071,7547,7657,7777,8000,8069,8080,8087,8089,8090,8098,8129,
	8139,8140,8181,8333,8443,8834,8888,9000,9051,9100,9151,9160,9200,9600,9943,
	9944,9981,9999,10000,10001,10243,11211,16010,18245,18246,20000,20547,25565,
	27017,28017,32764,44818,47808,49152,50100,55553,55554,62078,64738"""

	#port_arg = '-p 80'

    #Instantiate nmap scanner.
	nm = nmap.PortScanner()


	print "Initiating nmap scan for all public ip addresses."
	print "If this phase hangs, public ips may be inaccessible, or behind a firewall."
	print "\n------------------------------------------------------------------"
	print('------------------------------------------------------------------\n')
	#Iterate over both IPs and instance names together
	for host_name, host_ip in public_ips.iteritems():

		
		#Initiate initial nmap scan with given arguments
		print "Scanning {} over the IP address {}".format(host_name, host_ip)
		
		nm.scan(hosts=host_ip, arguments='-Pn {}'.format(port_arg[0]))
		#p = multiprocessing.Process(target=nm.scan,args=(hosts=host_ip, arguments='-Pn {}'.format(port_arg[0])))

		#General separator
		print('------------------------------------------------------------------\n')

		try:

			#Pull relevant data from nmap scan
			host_name_address, ssl_scan_needed = perform_nmap(host_ip, nm)

			#If needed, perform additional ssllabs-scan
			if ssl_scan_needed == True:
				ssllabs_scan_result = perform_ssllabs_scan(host_name_address, False)
				#Log results
				print(ssllabs_scan_result)
			print "\n"


		#Exception is thrown if nmap cannot find the host.		
		except KeyError as e:
			print('Host \"{}\" ({}) looks down from here.\n'.format(host_name, host_ip))