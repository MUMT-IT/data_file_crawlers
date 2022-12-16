import requests
import glob
import win32wnet
import os
import sys
import tomli
import click


@click.command()
@click.argument('folder')
@click.option('--remote/--local', default=True)
@click.option('--dry/--not-dry', default=False)
def main(folder, dry, remote):
    folder = r'{}'.format(folder)
    if remote:
        net_resource = win32wnet.NETRESOURCE()
        net_resource.lpRemoteName = folder
        try:
            print('Connecting to the remote resource..')
            win32wnet.WNetAddConnection2(net_resource, 'Genius02', 'nut')
        except Exception as err:
            if isinstance(err, win32wnet.error):
                # Disconnect previous connections if detected, and reconnect.
                if err[0] == 1219:
                    win32wnet.WNetCancelConnection2(folder, 0, 0)
                    win32wnet.WNetAddConnection2(net_resource, 'Genius02', 'nut')
            raise err
        else:
            print('Remote resource is connected.')

    new_root = ''
    for root, dirs, filenames in os.walk(folder):
        curr_root = root

        if curr_root != new_root:
            print('Change folder, reset dataset reference..', curr_root, new_root)
            dataset_ref = ''
            for fn in filenames:
                if fn == 'info.toml':
                    print('\t\tInfo file found.')
                    with open(os.path.join(root, 'info.toml'), 'rb') as fp:
                        info = tomli.load(fp)
                        dataset_ref = info['dataset']['ref']
                        print(f'dataset ref = {dataset_ref}')
                        new_root = curr_root
                    continue
                update_datetime = os.path.getmtime(os.path.join(root, fn))
                create_datetime = os.path.getctime(os.path.join(root, fn))
                data_file = {'dataset_ref': dataset_ref,
                             'name': fn,
                             'create_datetime': create_datetime,
                             'update_datetime': update_datetime,
                             'url': os.path.join(root, fn)
                             }
                if not dry:
                    if dataset_ref:
                        resp = requests.post('https://mumtmis.herokuapp.com/data-blueprint/api/v1.0/data-file', json=data_file)
                        if resp.status_code != 201:
                            print(resp.status_code)
                        else:
                            print(f'Finished uploading {fn}.')
                            print(resp.status_code)
                else:
                    if dataset_ref:
                        print(f'**Sending data of {fn}..')
    if remote:
        win32wnet.WNetCancelConnection2(folder, 0, 0)


if __name__ == '__main__':
    main()