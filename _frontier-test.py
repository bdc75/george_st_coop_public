

page.goto("https://wholesale.frontiercoop.com/")
page.get_by_role("link", name="Sign In/Create Account").click()
page.get_by_role("textbox", name="Email*").fill("ordering@georgestreetcoop.com")
page.get_by_label("Password", exact=True).fill("Cardwell=27")
page.get_by_role("button", name="Sign In").click()
page.goto("https://wholesale.frontiercoop.com/data-feeds/")
with page.expect_download() as download_info:
    page.get_by_role("link", name="Wholesale Catalog (Excel)").click()
download = download_info.value
with page.expect_download() as download1_info:
    page.get_by_role("link", name="Monthly Specials (Excel)").click()
download1 = download1_info.value