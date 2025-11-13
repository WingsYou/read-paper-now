#!/usr/bin/env python3
"""
Paper Information Fetcher
Fetches paper information from arXiv, Google Scholar, Semantic Scholar, and other sources
Format: **Paper Title** FirstAuthor et al. Year. Venue. Citations: N
"""

import sys
import re
import requests
from bs4 import BeautifulSoup
import json
import argparse
import time

# Set request headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Debug mode flag
DEBUG_MODE = False


def fetch_arxiv_info_from_web(arxiv_id):
    """Fetch paper info from arXiv web page (fallback method)"""
    try:
        url = f"https://arxiv.org/abs/{arxiv_id}"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Title
        title_elem = soup.find('h1', class_='title')
        if not title_elem:
            return None
        title = title_elem.text.replace('Title:', '').strip()

        # Authors
        authors = []
        authors_elem = soup.find('div', class_='authors')
        if authors_elem:
            for author in authors_elem.find_all('a'):
                authors.append(author.text.strip())

        # Date
        dateline = soup.find('div', class_='dateline')
        year = 'N/A'
        if dateline:
            date_match = re.search(r'(\d{4})', dateline.text)
            if date_match:
                year = date_match.group(1)

        # Comments may contain venue information
        venue = 'arXiv'
        comments = soup.find('td', class_='tablecell comments')
        if comments:
            comment_text = comments.text
            # Try to identify common conferences/journals
            for conf in ['NeurIPS', 'ICLR', 'ICML', 'CVPR', 'ICCV', 'ECCV', 'ACL', 'EMNLP', 'AAAI']:
                if conf in comment_text:
                    venue = conf
                    # Try to extract year
                    year_match = re.search(rf'{conf}\s*(\d{{4}})', comment_text)
                    if year_match:
                        year = year_match.group(1)
                    break

        return {
            'title': title,
            'authors': authors,
            'year': year,
            'venue': venue,
            'citations': 'N/A'  # No citation count on web page
        }
    except Exception as e:
        print(f"Error fetching arXiv web info: {e}", file=sys.stderr)
        return None


def fetch_arxiv_info(arxiv_id):
    """Fetch paper information from arXiv API"""
    try:
        # First try to fetch from web page (more reliable)
        info = fetch_arxiv_info_from_web(arxiv_id)
        if info:
            return info

        # Fallback: try API
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"arXiv API returned status {response.status_code}", file=sys.stderr)
            return None

        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)

        # Namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entry = root.find('atom:entry', ns)
        if entry is None:
            return None

        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')

        # Get authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns).text
            authors.append(name)

        # Publication time
        published = entry.find('atom:published', ns).text[:4]  # Year

        return {
            'title': title,
            'authors': authors,
            'year': published,
            'venue': 'arXiv',
            'citations': 'N/A'
        }
    except Exception as e:
        print(f"Error fetching arXiv info: {e}", file=sys.stderr)
        return None


def get_citations_from_semantic_scholar(arxiv_id=None, doi=None, title=None):
    """Get citation count from Semantic Scholar API"""
    try:
        base_url = "https://api.semanticscholar.org/graph/v1/paper/"

        if arxiv_id:
            paper_id = f"arXiv:{arxiv_id}"
        elif doi:
            paper_id = f"DOI:{doi}"
        elif title:
            # Search paper
            search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {'query': title, 'limit': 1, 'fields': 'citationCount,title,authors,year,venue'}
            response = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    return data['data'][0].get('citationCount', 'N/A')
            return 'N/A'
        else:
            return 'N/A'

        # Get paper information
        url = f"{base_url}{paper_id}"
        params = {'fields': 'citationCount,title,authors,year,venue'}
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get('citationCount', 'N/A')

        return 'N/A'
    except Exception as e:
        print(f"Warning: Could not fetch citation count: {e}", file=sys.stderr)
        return 'N/A'


def get_citations_from_google_scholar(title):
    """Get citation count from Google Scholar"""
    try:
        import urllib.parse

        # Build search URL
        query = urllib.parse.quote(title)
        url = f"https://scholar.google.com/scholar?q={query}"

        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"Google Scholar returned status {response.status_code}", file=sys.stderr)
            return 'N/A'

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find first search result
        results = soup.find_all('div', class_='gs_ri')
        if not results:
            return 'N/A'

        # Find citation info below first result
        first_result = results[0]
        # Google Scholar citation link format: "Cited by XXX"
        cite_link = soup.find('a', string=re.compile(r'Cited by \d+'))

        if cite_link:
            cite_text = cite_link.text
            match = re.search(r'Cited by (\d+)', cite_text)
            if match:
                return int(match.group(1))

        return 'N/A'
    except Exception as e:
        print(f"Warning: Could not fetch Google Scholar citations: {e}", file=sys.stderr)
        return 'N/A'


def search_google_scholar(title):
    """Search Google Scholar and get complete paper information"""
    try:
        import urllib.parse

        # Build search URL
        query = urllib.parse.quote(title)
        url = f"https://scholar.google.com/scholar?q={query}"

        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"Google Scholar search returned status {response.status_code}", file=sys.stderr)
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find first search result
        results = soup.find_all('div', class_='gs_ri')
        if not results:
            print("No results found in Google Scholar", file=sys.stderr)
            return None

        first_result = results[0]

        # Title
        title_elem = first_result.find('h3', class_='gs_rt')
        if not title_elem:
            return None
        title_text = title_elem.get_text().strip()
        # Remove possible [PDF] or [BOOK] prefix
        title_text = re.sub(r'^\[(PDF|BOOK|HTML)\]\s*', '', title_text)

        # Authors and publication info
        authors = []
        year = 'N/A'
        venue = 'Unknown'

        info_elem = first_result.find('div', class_='gs_a')
        if info_elem:
            info_text = info_elem.get_text()
            if DEBUG_MODE:
                print(f"Debug: gs_a text = {info_text}", file=sys.stderr)

            # Format is usually: "Author - Source, Year - Publisher"
            # Or it may be: "Author - Source - Publisher"
            parts = info_text.split(' - ')

            if len(parts) > 0:
                # Extract authors
                author_text = parts[0].strip()
                author_list = author_text.split(',')
                authors = [a.strip() for a in author_list if a.strip() and len(a.strip()) > 1]

            if len(parts) > 1:
                # Extract year - search in entire string
                year_match = re.search(r'\b(19|20)\d{2}\b', info_text)
                if year_match:
                    year = year_match.group(0)

                # Extract venue - usually in second part
                venue_text = parts[1].strip()
                # Remove year
                venue_text = re.sub(r',?\s*(19|20)\d{2}', '', venue_text).strip()
                # Remove possible trailing punctuation
                venue_text = venue_text.rstrip(',-')

                if venue_text and len(venue_text) > 1:
                    venue = venue_text
                    # Standardize common venue names
                    if 'arxiv' in venue.lower():
                        venue = 'arXiv'
                    elif 'openreview' in venue.lower():
                        venue = 'OpenReview'

        # Citation count - improved search logic
        citations = 'N/A'

        # Method 1: Find citation links in entire result
        try:
            # Find container with current result
            result_container = first_result.parent
            if result_container:
                # Find citation info in container
                cite_links = result_container.find_all('a')
                for link in cite_links:
                    if link.text and 'Cited by' in link.text:
                        match = re.search(r'Cited by (\d+)', link.text)
                        if match:
                            citations = int(match.group(1))
                            break
        except Exception as e:
            if DEBUG_MODE:
                print(f"Debug: Method 1 failed: {e}", file=sys.stderr)

        # Method 2: Search directly after first result
        if citations == 'N/A':
            try:
                # gs_fl contains citation, save and other links
                gs_fl = soup.find_all('div', class_='gs_fl')
                for fl in gs_fl:
                    cite_link = fl.find('a', string=re.compile(r'Cited by \d+'))
                    if cite_link:
                        match = re.search(r'Cited by (\d+)', cite_link.text)
                        if match:
                            citations = int(match.group(1))
                            break
            except Exception as e:
                if DEBUG_MODE:
                    print(f"Debug: Method 2 failed: {e}", file=sys.stderr)

        if DEBUG_MODE:
            print(f"Debug: Parsed - year={year}, venue={venue}, citations={citations}", file=sys.stderr)

        return {
            'title': title_text,
            'authors': authors,
            'year': year,
            'venue': venue,
            'citations': citations
        }
    except Exception as e:
        print(f"Error searching Google Scholar: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None


def get_semantic_scholar_info(paper_id):
    """Get paper information directly from Semantic Scholar"""
    try:
        base_url = "https://api.semanticscholar.org/graph/v1/paper/"
        url = f"{base_url}{paper_id}"
        params = {'fields': 'citationCount,title,authors,year,venue,publicationVenue'}

        response = requests.get(url, params=params, headers=HEADERS, timeout=10)

        time.sleep(0.1)  # Avoid API rate limiting

        if response.status_code == 200:
            data = response.json()

            # Get venue information
            venue = data.get('venue', 'Unknown')
            if not venue and data.get('publicationVenue'):
                venue = data['publicationVenue'].get('name', 'Unknown')
            if not venue:
                venue = 'Unknown'

            return {
                'title': data.get('title', 'Unknown'),
                'authors': [author.get('name') for author in data.get('authors', [])],
                'year': str(data.get('year', 'N/A')),
                'venue': venue,
                'citations': data.get('citationCount', 'N/A')
            }

        return None
    except Exception as e:
        print(f"Error fetching Semantic Scholar info: {e}", file=sys.stderr)
        return None


def parse_url(url):
    """Parse URL, identify source and extract paper ID"""
    # arXiv
    arxiv_pattern = r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)'
    match = re.search(arxiv_pattern, url)
    if match:
        return ('arxiv', match.group(1))

    # Semantic Scholar
    ss_pattern = r'semanticscholar\.org/paper/(?:[^/]+/)?([a-f0-9]+)'
    match = re.search(ss_pattern, url)
    if match:
        return ('semantic_scholar', match.group(1))

    # OpenReview (supports more characters, including underscores and hyphens)
    or_pattern = r'openreview\.net/(?:forum|pdf)\?id=([A-Za-z0-9_\-]+)'
    match = re.search(or_pattern, url)
    if match:
        return ('openreview', match.group(1))

    # DOI
    doi_pattern = r'doi\.org/(10\.\d+/[^\s]+)'
    match = re.search(doi_pattern, url)
    if match:
        return ('doi', match.group(1))

    return (None, None)


def fetch_openreview_info(paper_id):
    """Fetch paper information from OpenReview"""
    try:
        # OpenReview API
        url = f"https://api.openreview.net/notes?id={paper_id}"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        if not data.get('notes') or len(data['notes']) == 0:
            return None

        note = data['notes'][0]
        content = note.get('content', {})

        title = content.get('title', 'Unknown')
        authors = content.get('authors', [])

        # Infer year from venue
        venue = note.get('invitation', '')
        year_match = re.search(r'20\d{2}', venue)
        year = year_match.group(0) if year_match else 'N/A'

        # Infer venue name
        venue_name = 'OpenReview'
        if 'ICLR' in venue:
            venue_name = 'ICLR'
        elif 'NeurIPS' in venue:
            venue_name = 'NeurIPS'
        elif 'ICML' in venue:
            venue_name = 'ICML'

        # Try to get citation count
        citations = get_citations_from_semantic_scholar(title=title)

        return {
            'title': title,
            'authors': authors,
            'year': year,
            'venue': venue_name,
            'citations': citations
        }
    except Exception as e:
        print(f"Error fetching OpenReview info: {e}", file=sys.stderr)
        return None


def format_authors(authors, max_authors=3):
    """Format author list, similar to ICLR citation format"""
    if not authors:
        return "Unknown Authors"

    if len(authors) <= max_authors:
        # Extract last name
        formatted = []
        for author in authors:
            parts = author.split()
            if len(parts) > 1:
                # Last name is at the end
                last_name = parts[-1]
                # Initials (no trailing period, handled uniformly by format_output)
                initials = '. '.join([p[0] for p in parts[:-1]])
                formatted.append(f"{last_name}, {initials}.")
            else:
                formatted.append(author)

        result = ""
        if len(formatted) == 1:
            result = formatted[0]
        elif len(formatted) == 2:
            result = f"{formatted[0]} and {formatted[1]}"
        else:
            result = ', '.join(formatted[:-1]) + f', and {formatted[-1]}'

        # Remove trailing period (if any), added uniformly by format_output
        return result.rstrip('.')
    else:
        # Only show first author et al.
        parts = authors[0].split()
        if len(parts) > 1:
            last_name = parts[-1]
            initials = '. '.join([p[0] for p in parts[:-1]]) + '.'
            return f"{last_name}, {initials} et al"  # No period, will be added uniformly later
        else:
            return f"{authors[0]} et al"  # No period, will be added uniformly later


def format_output(paper_info, max_authors=3):
    """Format output"""
    if not paper_info:
        return "Error: Could not fetch paper information"

    title = paper_info['title']
    authors = format_authors(paper_info['authors'], max_authors=max_authors)
    year = paper_info['year']
    venue = paper_info['venue']
    citations = paper_info['citations']

    # Format: **Title** Authors. Year. Venue. Citations: N
    return f"**{title}** {authors}. {year}. {venue}. Citations: {citations}"


def get_test_paper_info(test_id):
    """Return test paper information"""
    test_papers = {
        '1': {
            'title': 'Attention Is All You Need',
            'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar', 'Jakob Uszkoreit', 'Llion Jones', 'Aidan N. Gomez', 'Lukasz Kaiser', 'Illia Polosukhin'],
            'year': '2017',
            'venue': 'NeurIPS',
            'citations': 98234
        },
        '2': {
            'title': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
            'authors': ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee', 'Kristina Toutanova'],
            'year': '2019',
            'venue': 'NAACL',
            'citations': 67890
        },
        '3': {
            'title': 'Learning Transferable Visual Models From Natural Language Supervision',
            'authors': ['Alec Radford', 'Jong Wook Kim', 'Chris Hallacy', 'Aditya Ramesh', 'Gabriel Goh', 'Sandhini Agarwal', 'Girish Sastry', 'Amanda Askell'],
            'year': '2021',
            'venue': 'ICML',
            'citations': 15678
        }
    }
    return test_papers.get(test_id)


def main():
    parser = argparse.ArgumentParser(description='Fetch paper information and format output')
    parser.add_argument('url', help='Paper link (supports arXiv, Semantic Scholar, OpenReview) or paper title (--google-scholar) or test ID (--test 1/2/3)')
    parser.add_argument('--max-authors', type=int, default=3, help='Maximum number of authors to display')
    parser.add_argument('--test', action='store_true', help='Use test data (offline mode)')
    parser.add_argument('--google-scholar', action='store_true', help='Use Google Scholar search (input paper title)')
    parser.add_argument('--use-google-scholar-citations', action='store_true', help='Prioritize Google Scholar for citation counts (more accurate but slower)')
    parser.add_argument('--debug', action='store_true', help='Show debug information')

    args = parser.parse_args()

    # Set global debug flag
    global DEBUG_MODE
    DEBUG_MODE = args.debug

    # Test mode
    if args.test:
        paper_info = get_test_paper_info(args.url)
        if not paper_info:
            print(f"Error: Test ID '{args.url}' not found. Available: 1, 2, 3", file=sys.stderr)
            print("\nTest papers:", file=sys.stderr)
            print("  1: Attention Is All You Need", file=sys.stderr)
            print("  2: BERT", file=sys.stderr)
            print("  3: CLIP", file=sys.stderr)
            sys.exit(1)
        output = format_output(paper_info, max_authors=args.max_authors)
        print(output)
        return

    # Google Scholar search mode
    if args.google_scholar:
        paper_info = search_google_scholar(args.url)
        if not paper_info:
            print(f"Error: Could not find paper on Google Scholar", file=sys.stderr)
            sys.exit(1)
        output = format_output(paper_info, max_authors=args.max_authors)
        print(output)
        return

    # Parse URL
    source, paper_id = parse_url(args.url)

    if not source:
        print(f"Error: Unsupported URL format: {args.url}", file=sys.stderr)
        print("Supported sources: arXiv, Semantic Scholar, OpenReview", file=sys.stderr)
        print("Or use --google-scholar flag to search by title", file=sys.stderr)
        sys.exit(1)

    # Get information based on source
    paper_info = None

    if source == 'arxiv':
        paper_info = fetch_arxiv_info(paper_id)
        # Add citation count
        if paper_info and paper_info.get('citations') == 'N/A':
            # Prioritize Google Scholar (if specified)
            if args.use_google_scholar_citations:
                citations = get_citations_from_google_scholar(paper_info['title'])
                if citations != 'N/A':
                    paper_info['citations'] = citations
                else:
                    # Google Scholar failed, try Semantic Scholar
                    citations = get_citations_from_semantic_scholar(arxiv_id=paper_id)
                    if citations != 'N/A':
                        paper_info['citations'] = citations
            else:
                # Use Semantic Scholar by default
                citations = get_citations_from_semantic_scholar(arxiv_id=paper_id)
                if citations != 'N/A':
                    paper_info['citations'] = citations
                else:
                    # Semantic Scholar failed, try Google Scholar
                    citations = get_citations_from_google_scholar(paper_info['title'])
                    if citations != 'N/A':
                        paper_info['citations'] = citations
    elif source == 'semantic_scholar':
        paper_info = get_semantic_scholar_info(paper_id)
        # If Google Scholar specified, try to update citation count
        if paper_info and args.use_google_scholar_citations and paper_info.get('title'):
            gs_citations = get_citations_from_google_scholar(paper_info['title'])
            if gs_citations != 'N/A':
                paper_info['citations'] = gs_citations
    elif source == 'openreview':
        paper_info = fetch_openreview_info(paper_id)
        # OpenReview citation counts may be inaccurate, try Google Scholar update
        if paper_info and paper_info.get('title'):
            if args.use_google_scholar_citations or paper_info.get('citations') == 'N/A':
                gs_citations = get_citations_from_google_scholar(paper_info['title'])
                if gs_citations != 'N/A':
                    paper_info['citations'] = gs_citations
    elif source == 'doi':
        # Search via Semantic Scholar
        paper_info = get_semantic_scholar_info(f"DOI:{paper_id}")
        # If Google Scholar specified, try to update citation count
        if paper_info and args.use_google_scholar_citations and paper_info.get('title'):
            gs_citations = get_citations_from_google_scholar(paper_info['title'])
            if gs_citations != 'N/A':
                paper_info['citations'] = gs_citations

    if not paper_info:
        print(f"Error: Could not fetch paper information from {source}", file=sys.stderr)
        sys.exit(1)

    # Format and output
    output = format_output(paper_info, max_authors=args.max_authors)
    print(output)


if __name__ == '__main__':
    main()
