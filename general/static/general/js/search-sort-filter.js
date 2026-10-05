// Автоматическая отправка формы фильтрации, сортировки и поиска без перезагрузки страницы.
// См. комментарий в templates/general/embedded/search_sort_filter.html


$('#id_sort, #id_filter').on('change', function() {
        $('#search-sort-filter').submit();
    });


$('#id_search').on('focusout', function() {
        $('#search-sort-filter').submit();
});
