#!/usr/bin/env python3
import argparse
import datetime
from unittest.mock import (
    MagicMock,
    Mock,
    call,
    patch,
)

import requests

# settings parameters
root_url = "https://app.cardiomatics.com/api/v2"
signal_status_keys = ['id', 'name', 'status', 'message']
DEBUG = False


def initialize_arguments_parser():
    # Initialize parser
    parser = argparse.ArgumentParser(prog="python3 ccc.py", description="Cardiomatics Console Client")

    parser.add_argument("-token", "--Token",
                        help="Providing token for authentications",
                        required=True)

    parser.add_argument("-name", "--SignalName",
                        help="Providing signal name", nargs='?', default="test")

    parser.add_argument("-upload", "--UploadSignal",
                        help="Uploading a signal (single recording file) to the Cardiomatics platform",
                        type=argparse.FileType('rb'))

    parser.add_argument('-uploads', "--UploadSignals",
                        help="Uploading few signals files to the Cardiomatics platform (separate reports)",
                        type=argparse.FileType('rb'), nargs='+')

    parser.add_argument('-complex', "--ComplexUploadSignal",
                        help="Uploading few signals files to the Cardiomatics platform (one report)",
                        type=argparse.FileType('rb'), nargs='+')

    parser.add_argument("-list", "--ListAllSignals",
                        help="Listing all signals in the Cardiomatics platform and its statuses",
                        nargs='?', const=True, default=False)

    parser.add_argument("-pdfs", "--DownloadAll",
                        help="Downloading all available PDF reports",
                        nargs='?', const=True, default=False)

    parser.add_argument("-new", "--DownloadNew",
                        help="Downloading only new PDF reports",
                        nargs='?', const=True, default=False)

    parser.add_argument("-rm", "--RemoveAll",
                        help="Delete all signals (for testing purposes)",
                        nargs='?', const=True, default=False)

    parser.add_argument("-debug", "--Debugging",
                        help="Show more printouts for debugging purposes",
                        nargs='?', const=True, default=False)

    return parser.parse_args()


class UrlsManager:
    # if the url API will be changed, here is the place to handle it

    def __init__(self, token, root_url):
        self.token = token
        self.root_url = root_url

    def get_signals(self, per_page=100, page=1):
        return f"{self.root_url}/signals?private_token={self.token}&per_page={per_page}&page={page}"

    def post_signal(self):
        return f"{self.root_url}/signals?private_token={self.token}"

    def get_signal_by_id(self, sig_id):
        return f"{self.root_url}/signals/{sig_id}?private_token={self.token}"

    def get_signal_printout(self, sig_id):
        return f"{self.root_url}/signals/{sig_id}/report/printout?private_token={self.token}"


class SignalsManager:

    def __init__(self, urls_manager):
        self.urls_manager = urls_manager

    def send_init_signal(self, values):
        # curl --request POST --header "PRIVATE-TOKEN: <token>" --data "name=test&file_names_list=RECORD.GTM" root_url
        response = requests.post(self.urls_manager.post_signal(), data=values)
        response_dict = response.json()
        debug(response_dict)
        return response_dict

    def upload_files(self, url, post_fields, signal_file):
        # curl --request POST --form post_fields --form "file=@RECORD.GTM" url
        response = requests.post(url, data=post_fields, files={'file': signal_file})
        debug(response.text)

    def get_all_signals(self):
        all_signals = []
        current_page_signals = ["init"]
        page = 1
        while len(current_page_signals) != 0:
            response = requests.get(self.urls_manager.get_signals(per_page=10, page=page))
            current_page_signals = response.json()
            if current_page_signals:
                debug(f"Page: {page}, signals:{len(current_page_signals)}")
                page += 1
                all_signals.extend(current_page_signals)
        return all_signals

    def delete_signals(self, all_signals):
        # Signal removal for type Standard users is possible
        # only before analysis is started or when signal status is Error.
        # Admin anytime.
        signals_ids = [s['id'] for s in all_signals]
        debug(f"Deleting signals: {signals_ids}")
        if all_signals:
            for signal_data in all_signals:
                signal_id = signal_data.get('id')
                response = requests.delete(self.urls_manager.get_signal_by_id(signal_id))
                debug(response.status_code)
                if response.status_code == 204:
                    io_print(f"Signal no. {signal_id} deleted successfully")
        else:
            io_print("No signals, or no signal loaded upfront by 'ListAllSignals'. Use with option -list")

    def download_all_reports(self):
        pdfs_data = self._download_all_reports_data()
        download_all_pdfs(pdfs_data)

    def download_new_reports(self):
        new_pdfs_data = self._download_all_reports_data(filter_new=True)
        download_all_pdfs(new_pdfs_data)

    def _download_all_reports_data(self, filter_new=False):
        pdfs_data = []
        signals_data = self.get_all_signals()
        if filter_new is True:
            signals_data = [signal_data for signal_data in signals_data if signal_data.get('new') is True]
        for signal_data in signals_data:
            signal_id = signal_data.get('id')
            signal_status = signal_data.get("status")
            debug(f"Signal status: {signal_status}")
            if signal_status in ["Done", "Warning"]:
                response = requests.get(self.urls_manager.get_signal_printout(signal_id))
                signal_report = response.json()
                pdfs_data.append(signal_report)
        debug(f"pdfs_data: {pdfs_data}")
        return pdfs_data


def download_all_pdfs(pdfs_data):
    i = 1
    n = len(pdfs_data)
    io_print(f"Downloading {n} reports")
    for pdf_data in pdfs_data:
        report_name = pdf_data.get('name')
        io_print(f"[{i}/{n}] {report_name}")
        download_file(report_name, pdf_data.get('url'))
        i += 1


def download_file(name, url):
    response = requests.get(url)
    pdf = open(name, 'wb')
    pdf.write(response.content)
    pdf.close()


def io_print(msg):
    # here is a good place to use ex. logger instead of print
    # or both
    print(msg)


def debug(msg):
    if DEBUG:
        io_print(f"DEBUG >>>>>> {msg}")


def print_signal_properties(all_signals):
    # here is a place where we can easily change
    # the format of presented data
    debug(all_signals)
    for signal_data in all_signals:
        signal_status = ""
        for key in signal_status_keys:
            val = signal_data.get(key)
            if val:
                signal_status += f"{key}: {val}\n"
        io_print(signal_status)


def upload_single_file(signal_manager, file_object, signal_file):
    post_url = file_object.get('url')
    debug(post_url)
    post_fields = file_object.get('post_fields')
    debug(post_fields)
    signal_manager.upload_files(post_url, post_fields, signal_file)


def upload_init_data(signal_manager, file_names_list, signal_name):
    time = datetime.datetime.now().strftime("%H_%M_%S")
    values = {'name': f'{time}_{signal_name}', 'file_names_list': file_names_list, 'autostart_analysis': True}
    return signal_manager.send_init_signal(values)


def upload_signal(signal_manager, signal_file, signal_name="test"):
    response_dict = upload_init_data(signal_manager, signal_file.name, signal_name)
    file_object = response_dict.get('files')[0]
    upload_single_file(signal_manager, file_object, signal_file)


def complex_uploads_signal(signal_manager, signal_files, signal_name="complex reports"):
    signal_files_names_csv = ",".join([signal_file.name for signal_file in signal_files])
    debug(signal_files_names_csv)
    response_dict = upload_init_data(signal_manager, signal_files_names_csv, signal_name)

    file_objects = response_dict.get('files')
    for file_object, signal_file in zip(file_objects, signal_files):
        upload_single_file(signal_manager, file_object, signal_file)


def get_signal_manager_or_exit(token, url_root):
    if token:
        urls_manager = UrlsManager(token, url_root)
        return SignalsManager(urls_manager)
    else:
        io_print("Requirement: Authorisation Token is needed for further script usage")
        exit(0)


def main():
    args = initialize_arguments_parser()
    global DEBUG
    DEBUG = True if args.Debugging else False
    signal_name = args.SignalName
    signal_manager = get_signal_manager_or_exit(args.Token, root_url)

    # required: single recording file
    if args.UploadSignal:
        upload_signal(signal_manager, args.UploadSignal, signal_name)

    # many separate recording file
    if args.UploadSignals:
        for signal_file in args.UploadSignals:
            upload_signal(signal_manager, signal_file, signal_name)

    # many recording file for one report
    if args.ComplexUploadSignal:
        complex_uploads_signal(signal_manager, args.ComplexUploadSignal, signal_name)

    all_signals = []
    if args.ListAllSignals:
        all_signals = signal_manager.get_all_signals()
        print_signal_properties(all_signals)

    if args.RemoveAll:
        signal_manager.delete_signals(all_signals)

    if args.DownloadAll:
        signal_manager.download_all_reports()

    if args.DownloadNew:
        signal_manager.download_new_reports()


if __name__ == '__main__':
    """
    Read arguments from command line
    a. uploading a signal (single recording file) to the Cardiomatics platform,
    b. listing all signals in the Cardiomatics platform and its statuses,
    c. downloading all available PDF reports,
    d. downloading only new PDF reports.
    """
    main()


def test_get_signal_manager_or_exit():
    token = "asdasd"
    url_root = "https://test.com/api/v2"
    sm = get_signal_manager_or_exit(token, url_root)
    assert type(sm) == SignalsManager


@patch.object(SignalsManager, 'send_init_signal')
def test_send_init_signal(signals_manager_mock, monkeypatch):
    # given
    datetime_mock = MagicMock(wrap=datetime.datetime)
    datetime_mock.now.return_value = datetime.datetime(2022, 1, 30, 16, 34, 9)
    monkeypatch.setattr(datetime, "datetime", datetime_mock)
    token = "asdasd"
    url_root = "https://test.com/api/v2"
    file_names_list = ["test.GTM", 'test2.GTM']
    signal_name = "test_name"

    # when
    url_manager = UrlsManager(token, url_root)
    signal_manager = SignalsManager(url_manager)

    # then
    upload_init_data(signal_manager, file_names_list, signal_name)
    assert signals_manager_mock.mock_calls == [
        call({
            'name': '16_34_09_test_name',
            'file_names_list': ['test.GTM', 'test2.GTM'],
            'autostart_analysis': True})
    ]


@patch.object(SignalsManager, 'send_init_signal')
def test_time_mocking(signals_manager_mock):
    # given
    datetime_mock = Mock(wraps=datetime.datetime)
    datetime_mock.now.return_value = datetime.datetime(2022, 1, 30, 16, 34, 9)

    token = "asdasd"
    url_root = "https://test.com/api/v2"
    file_names_list = ["test.GTM", 'test2.GTM']
    signal_name = "test_name"

    # when
    url_manager = UrlsManager(token, url_root)
    signal_manager = SignalsManager(url_manager)

    with patch('datetime.datetime', new=datetime_mock):
        # then
        upload_init_data(signal_manager, file_names_list, signal_name)
        assert signals_manager_mock.mock_calls == [
            call({
                'name': '16_34_09_test_name',
                'file_names_list': ['test.GTM', 'test2.GTM'],
                'autostart_analysis': True})
        ]
