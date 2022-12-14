import requests
import glob
import os
import sys
import tomli


def main(folder):
    for root, dirs, filenames in os.walk(folder):
        with open(os.path.join(root, 'info.toml'), 'rb') as fp:
            info = tomli.load(fp)
            dataset_ref = info['dataset']['ref']
            for fn in filenames:
                if fn == 'info.toml':
                    continue
                update_datetime = os.path.getmtime(os.path.join(root, fn))
                create_datetime = os.path.getctime(os.path.join(root, fn))
                data_file = {'dataset_ref': dataset_ref,
                             'name': fn,
                             'create_datetime': create_datetime,
                             'update_datetime': update_datetime,
                             # 'url': os.path.join(root, fn)
                             }
                resp = requests.post('http://127.0.0.1:5000/data-blueprint/api/v1.0/data-file', json=data_file)
                if resp.status_code != 201:
                    print(resp.json())
                else:
                    print(f'Finished uploading {fn}.')
                    print(resp.status_code)


if __name__ == '__main__':
    folder = sys.argv[1]
    main(folder)