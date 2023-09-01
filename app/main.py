from typing import Any

# # externals
from packaging.version import Version
from rich import print
from typer import Typer
import httpx

app = Typer()

BASE_URL = 'https://pypi.org/pypi/{package}/json'


def license_metadata(classifiers: list[str]) -> str:
    for classifier in classifiers:
        if 'License' in classifier:
            return classifier
    return ''

def last_release(releases: dict[str, Any]) -> dict[str, str]:
    release = sorted(releases, key=Version)[-1]
    return {
        'relase': release, 
        'date': releases[release][0]['upload_time']
    }

def first_release(releases: dict[str, Any]) -> dict[str, str]:
    release = sorted(releases, key=Version)[0]
    try:
        return {
            'release': release,
            'date': releases[release][0]['upload_time'],
        }
    except KeyError:
        return {'release': release, 'data': ''}

def get_package_data(package: str) -> dict[str, Any]:
    url = BASE_URL.format(package=package)
    try:
        with httpx.Client() as client:
            response = client.get(url, timeout=None)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        print(f"Erro ao fazer a solicitação HTTP: {e}")
    except httpx.HTTPStatusError as e:
        print(f"Erro de HTTP: {e}")
    except Exception as e:
        print(f"Erro desconhecido: {e}")
    return {}

@app.command()
def package_data(package: str) -> None:
    data = get_package_data(package)

    if not data:
        print(f"Pacote '{package}' não encontrado.")
        return

    license = license_metadata(data.get('info', {}).get('classifiers', []))
    releases = data.get('releases', {})
    
    release_info = []
    for version, release_data in releases.items():
        upload_time = release_data[0].get('upload_time', '')
        release_info.append({'version': version, 'date': upload_time})
    
    url = data.get('info', {}).get('package_url', '') + '#history'
    
    print(
        {
            'package': package,
            'url': url,
            'licença': license,
            'releases': release_info,
        }
    )


if __name__ == '__main__':
    app()