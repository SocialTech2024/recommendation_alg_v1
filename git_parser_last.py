import pandas as pd
import requests
import time

token = '123'

file_path = 'analys.xlsx' 
df = pd.read_excel(file_path)

def extract_github_username(url):
    if pd.isna(url) or 'github.com' not in url:
        return None
    return url.split('github.com/')[-1].split('/')[0]

df['GitHub_Username'] = df['GitHub'].apply(extract_github_username)

def get_github_data(username, token):
    headers = {'Authorization': f'token {token}'}
    base_url = f'https://api.github.com/users/{username}'

    profile_response = requests.get(base_url, headers=headers)
    if profile_response.status_code != 200:
        print(f"Не удалось получить данные для пользователя: {username}")
        return None

    repos_url = f'{base_url}/repos'
    repos_response = requests.get(repos_url, headers=headers)
    
    if repos_response.status_code != 200:
        print(f"Ошибка при запросе репозиториев пользователя {username}: {repos_response.text}")
        return None
    
    try:
        repos_data = repos_response.json()
    except ValueError:
        print(f"Ошибка преобразования ответа в JSON для пользователя {username}: {repos_response.text}")
        return None

    if not isinstance(repos_data, list):
        print(f"Неправильный формат данных репозиториев для пользователя {username}: {repos_data}")
        return None

    repo_count = 0
    popular_repos = 0
    languages = set()
    total_stars = 0
    total_forks = 0

    for repo in repos_data:
        repo_name = repo['name']
        repo_count += 1
        total_stars += repo.get('stargazers_count', 0)
        total_forks += repo.get('forks_count', 0)

        if repo.get('stargazers_count', 0) >= 10:
            popular_repos += 1

        languages_url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
        languages_response = requests.get(languages_url, headers=headers)
        try:
            repo_languages = languages_response.json()
            languages.update(repo_languages.keys())
        except ValueError:
            print(f"Ошибка преобразования данных языков в JSON для репозитория {repo_name} пользователя {username}")


    return {
        'GitHub_Repo_Count': repo_count,
        'GitHub_Total_Stars': total_stars,
        'GitHub_Total_Forks': total_forks,
        'GitHub_Popular_Repos': popular_repos,
        'GitHub_Languages': ', '.join(languages)
    }

df['GitHub_Repo_Count'] = None
df['GitHub_Total_Stars'] = None
df['GitHub_Total_Forks'] = None
df['GitHub_Popular_Repos'] = None
df['GitHub_Languages'] = None

for index, row in df.iterrows():
    username = row['GitHub_Username']
    if username:
        print(f"Получение данных для пользователя: {username}")
        github_data = get_github_data(username, token)
        
        if github_data:
            df.at[index, 'GitHub_Repo_Count'] = github_data['GitHub_Repo_Count']
            df.at[index, 'GitHub_Total_Stars'] = github_data['GitHub_Total_Stars']
            df.at[index, 'GitHub_Total_Forks'] = github_data['GitHub_Total_Forks']
            df.at[index, 'GitHub_Popular_Repos'] = github_data['GitHub_Popular_Repos']
            df.at[index, 'GitHub_Languages'] = github_data['GitHub_Languages']
        
     
        time.sleep(1)

df.to_excel('analys_with_github_data.xlsx', index=False)
print("Данные успешно сохранены в 'analys_with_github_data.xlsx'")