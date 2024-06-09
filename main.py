from Wappalyzer import Wappalyzer, WebPage
from Wappalyzer.technology import *
import json

def contains_in_any_form(data, word):
    """
    Check if the data contains the word in any form (case insensitive).
    Args:
        data (any): The data to check.
        word (str): The word to check for.
    Returns:
        bool: True if the word is found in the data, False otherwise.
    """
    word = word.lower()
    if isinstance(data, dict):
        for key, value in data.items():
            if contains_in_any_form(key, word) or contains_in_any_form(value, word):
                return True
    elif isinstance(data, list):
        for item in data:
            if contains_in_any_form(item, word):
                return True
    elif isinstance(data, str):
        if word in data.lower():
            return True
    return False


def extract_plugin_version(url, plugin_pattern, version_pattern):
    """
    Extract plugin and version from the URL based on given patterns.
    Args:
        url (str): The URL to extract data from.
        plugin_pattern (str): The regex pattern to extract the plugin.
        version_pattern (str): The regex pattern to extract the version.
    Returns:
        tuple: A tuple containing the plugin and version.
    """
    plugin = re.search(plugin_pattern, url)
    version = re.search(version_pattern, url)
    return (plugin.group(0) if plugin else None, version.group(0) if version else None)


def process_plugin(url, regex_plugin, regex_version,plugins):
    """
    Process a plugin from a given URL using the provided regular expressions.

    Args:
        url (str): The URL to extract the plugin information from.
        regex_plugin (str): The regular expression pattern to match the plugin name.
        regex_version (str): The regular expression pattern to match the plugin version.

    Returns:
        None

    """
    plugin, version = extract_plugin_version(url, regex_plugin, regex_version)
    if plugin:
        category = "JavaScript libraries" if '.js' in plugin else "WordPress plugins"
        if plugin not in plugins:
            plugins[plugin] = {"versions": set(), "categories": []}
        if version:
            plugins[plugin]["versions"].add(str(version).strip())
        if category not in plugins[plugin]["categories"]:
            plugins[plugin]["categories"].append(category)
    return plugins


def check_plugin_by_wordpress(analysis):
    """
    Check if the analysis contains references to WordPress and process the plugins found.

    Args:
        analysis (str): The analysis to check for WordPress references.

    Returns:
        dict: A dictionary containing information about the plugins found, including their versions.

    Raises:
        Exception: If an error occurs during the processing of plugins.

    """
    if contains_in_any_form(analysis, 'WordPress'):
        plugins = dict()
        try:
            data = filter_technology('test.txt', 'wp-content')
            for url in data:
                plugins = process_plugin(url, r"(?<=plugins/)[^/]*", r"(?<=ver=)[^&]*", plugins)

            data = filter_technology('test.txt', 'wp-includes')
            for url in data:
                plugins = process_plugin(url, r"(?<=/)[^/]*?(?=\?ver=)", r"(?<=ver=)[^&]*", plugins)

            for plugin in plugins:
                plugins[plugin]["versions"] = list(plugins[plugin]["versions"])

        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print('Not found')
        
    return plugins


def main():
    wappalyzer = Wappalyzer.latest(update=True)
    webpage = WebPage.new_from_url('http://www.chinafangwei.cn')
    wappalyzer.analyze_with_categories(webpage)
    analysis = wappalyzer.analyze_with_versions_and_categories(webpage)
    wordpress_plugins = check_plugin_by_wordpress(analysis)
    print(json.dumps({**analysis, **wordpress_plugins}, indent=4))


if __name__ == '__main__':
    main()




