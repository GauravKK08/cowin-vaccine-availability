import requests
import json
from pprint import pprint
from datetime import datetime

class PublicCowinAPIsWrapper():

    def __init__(self):
        self.api_server = "https://cdn-api.co-vin.in/api/"
        self.headers = {
            'accept': 'application/json',
            'content-Type': 'application/json',
            'authority': 'cdn-api.co-vin.in',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
            'origin': 'https://apisetu.gov.in',
            'referer': 'https://apisetu.gov.in/public/marketplace/api/cowin',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'sec-ch-ua': ' Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"'
            }
        self.txnId = None
        self.mobile = '9545665253'
        #self.userOTP = None
        self.today_date = datetime.now().strftime('%d-%m-%Y')
    
    def makeRequest(self, api_url_path, data={}, method='GET', raiseOnNotOK=True):

        url=self.api_server+api_url_path
        print('Hitting url: %s'%url)

        if method == 'GET':
            response = requests.get(url, headers=self.headers, params=data)
        elif method == 'POST':
            data = json.dumps(data) if data else {}
            response = requests.post(url, headers=self.headers, data=data)
        else:
            raise Exception('Unsupported request method: %s received.'%method)

        if response.status_code != 200:
            if raiseOnNotOK:
                raise Exception('Response Code:%s, Response: %s'%(response.status_code, response.text))
            else:
                return response.text
        response = response.json()
        if 'txnId' in response:
            self.txnId = response['txnId']
        return response

    def generateOTP(self):
        api_url_path = 'v2/auth/public/generateOTP'
        data = {'mobile': self.mobile}
        response = self.makeRequest(api_url_path, data=data, method='POST')
        #pprint(response)
        return response

    def confirmOTP(self, otp):
        api_url_path = 'v2/auth/public/confirmOTP'
        data = {'otp': otp, 'txnId': self.txnId}
        print('Sending data: %s'%data)
        response = self.makeRequest(api_url_path, data=data, method='POST')
        #pprint(response)
        return response

    def getStates(self):
        api_url_path = 'v2/admin/location/states'
        response = self.makeRequest(api_url_path, data={}, method='GET')

        ## List state with IDs & pretty prints them as well.
        states = response['states']
        print(states)
        state_names = [state['state_name'] for state in states]
        longest_state = max(state_names, key=lambda x:len(x))
        #print('Longest state: %s'%longest_state)
        print('State\t\t\t\tStateID')
        print('')
        print('-'*50)
        for state in states:
            state_name = state['state_name']
            state_id = state['state_id']
            row = '%s%s\t%s'%(state_name, (len(longest_state) - len(state_name))*' ', state_id)
            print(row)
        return response

    def getDistricts(self, state_id):
        api_url_path = 'v2/admin/location/districts/%s'%state_id
        response = self.makeRequest(api_url_path, data={}, method='GET')
        districts = response['districts']
        district_names = [district['district_name'] for district in districts]
        longest_district = max(district_names, key=lambda x:len(x))
        print('Longest district_name: %s'%longest_district)

        print('District\tDistrict ID')
        print('')
        print('-'*50)
        for district in districts:
            district_name = district['district_name']
            district_id = district['district_id']
            row = '%s%s\t%s'%(district_name, (len(longest_district) - len(district_name))*' ', district_id)
            print(row)
        return response

    def _prettyPrintSessionData(self, session):
        session_keys = ['name', 'address', 'available_capacity', 'available_capacity_dose1', 'available_capacity_dose2', 'slots']
        print('-'*50)
        data = {}
        for key in session_keys:
            if key == 'slots':
                data[key] = ', '.join(session[key])
            else:
                data[key] = session[key]
        pprint(data)
        print('-'*50)

    def _prettyPrintCentersData(self, center):
        center_keys = ['name', 'address']
        session_keys = ['available_capacity_dose1', 'available_capacity_dose2', 'slots', 'date']
        data = {}
        for key in center_keys:
            data[key] = center[key]
        sessions = center['sessions']
        pprint(data)
        for session in sessions:
            pprint('Date: %s, Dose1: %s, Dose2: %s'%(session['date'], session['available_capacity_dose1'], session['available_capacity_dose2']))

    def getVaccinationSessionsByDistrict(self, district_id, printAvailableSessions=False):
        api_url_path = 'v2/appointment/sessions/public/findByDistrict'
        data = {'district_id': district_id, 'date': self.today_date}
        response = self.makeRequest(api_url_path, data=data, method='GET')
        sessions = response['sessions']
        if printAvailableSessions:
            for session in sessions:
                if any([session['available_capacity_dose1'], session['available_capacity_dose2']]):
                    self._prettyPrintSessionData(session)
        return response

    def getVaccinationSessionsByPIN(self, pin_code, printAvailableSessions=False):
        api_url_path = 'v2/appointment/sessions/public/findByPin'
        data = {'pincode': pin_code, 'date': self.today_date}
        response = self.makeRequest(api_url_path, data=data, method='GET')
        sessions = response['sessions']
        if printAvailableSessions:
            for session in sessions:
                if any([session['available_capacity_dose1'], session['available_capacity_dose2']]):
                    self._prettyPrintSessionData(session)
        return response        

    def getVaccinationSessionsCalendarByPIN(self, pin_code):
        api_url_path = 'v2/appointment/sessions/public/calendarByPin'
        data = {'pincode': pin_code, 'date': self.today_date}
        response = self.makeRequest(api_url_path, data=data, method='GET')
        centers = response['centers']
        for center in centers:
            self._prettyPrintCentersData(center)
            print('')
        return response

    def getVaccinationSessionsCalendarByDistrict(self, district_id):
        api_url_path = 'v2/appointment/sessions/public/calendarByDistrict'
        data = {'district_id': district_id, 'date': self.today_date}
        response = self.makeRequest(api_url_path, data=data, method='GET')
        centers = response['centers']
        for center in centers:
            self._prettyPrintCentersData(center)
            print('')
        return response        

    ## Orchestrates the process.
    def go(self):
      
        """
        response = cowin.generateOTP()
        print('OTP successfully sent.')

        userOtp = input('Please enter OTP receveived on mobile:%s ->'%cowin.mobile)
        reponse = cowin.confirmOTP(otp=userOtp)
        print(response)
        """
        search_input = int(input('Search by: \n 1. PIN \n 2. State & District\n Enter 1 or 2\n'))
        pprint(search_input)
        if search_input == 2:
            response = self.getStates()
            states = response['states']
            state_ids = [state['state_id'] for state in states]
            while True:
                state_id = int(input('Please enter state_id from the above list: '))
                if state_id not in state_ids:
                    print('Not a valid stateID: %s. Please re-enter'%state_id)
                else:
                    self.state_id = state_id
                    break
            response = self.getDistricts(self.state_id)
            districts = response['districts']
            district_ids = [district['district_id'] for district in districts]
            while True:
                district_id = int(input('Please enter district_id from the above list: '))
                if district_id not in district_ids:
                    print('Not a valid stateID: %s. Please re-enter'%district_id)
                else:
                    self.district_id = district_id
                    break

            print('Received districtID:%s'%(self.district_id))
            self.getVaccinationSessionsByDistrict(district_id = self.district_id, printAvailableSessions=True)
            #self.getVaccinationSessionsCalendarByDistrict(district_id = self.district_id)
        elif search_input == 1:
            pin_code = input('Enter Pin code: ')
            self.getVaccinationSessionsByPIN(pin_code=pin_code, printAvailableSessions=True)
            #self.getVaccinationSessionsCalendarByPIN(pin_code=pin_code)
        else:
            raise Exception('Invalid search Input: %s'%search_input)

cowin = PublicCowinAPIsWrapper()
#cowin.district_id = 363
cowin.go()