// Make the master tables click-to-sort (MkDocs Material recipe).
document$.subscribe(function () {
  document.querySelectorAll("article table:not([class])").forEach(function (table) {
    new Tablesort(table);
  });
});
