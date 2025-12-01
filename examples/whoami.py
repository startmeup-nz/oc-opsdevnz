from oc_opsdevnz import OpenCollectiveClient

QUERY = """
query AccountBySlug($slug: String!) {
  account(slug: $slug) {
    id
    slug
    name
    type
  }
}
"""

if __name__ == "__main__":
    client = OpenCollectiveClient.for_staging()
    # Replace with your staging account/collective slug
    data = client.graphql(QUERY, {"slug": "opencollective"})
    print(data)
