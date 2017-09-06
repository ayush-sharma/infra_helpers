import argparse
import requests
import dns.resolver


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--elb_name', required=True, help='Value of ELB DNS.')
    parser.add_argument('--path', required=True,
                        help='Path to test for HTTP status code 200.')

    args = parser.parse_args()

    url = 'all.' + args.elb_name

    answers = dns.resolver.query(url, 'A')
    count = 1
    for ip in answers:

        ip = str(ip)
        test_request = 'http://' + ip + '/' + args.path

        request = requests.get(test_request)

        print(str(count) + '. ' + test_request + ' > ' + str(request.status_code))

        count += 1
