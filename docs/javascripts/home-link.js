// Material only links the header logo to home, not the site-name text beside it.
// Make the "Bring Me Hope Wiki" title clickable, reusing the logo's home href so
// it resolves correctly from any page depth.
document$.subscribe(function () {
  var name = document.querySelector(".md-header__title .md-ellipsis");
  if (!name || name.dataset.homeLinked) { return; }
  name.dataset.homeLinked = "1";
  name.style.cursor = "pointer";
  name.addEventListener("click", function () {
    var logo = document.querySelector("a.md-logo");
    window.location.href = logo ? logo.getAttribute("href") : ".";
  });
});
