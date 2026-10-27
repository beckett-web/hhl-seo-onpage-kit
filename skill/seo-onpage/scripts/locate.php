<?php
/* READ-ONLY (run with READONLY=1). For each path in getenv('URLS') (comma list): the WordPress object, its SEO meta,
   and every text-bearing Elementor element on it, including global templates it pulls in (shortcode, template
   widget, global widget, nested shortcodes) and the theme-builder templates that render it. Prints one JSON array. */
function els_walk($els, $cb, $path = []) {
  foreach ((array)$els as $i => $e) { $cb($e, $path); if (!empty($e['elements'])) els_walk($e['elements'], $cb, array_merge($path, [$e['id'] ?? $i])); }
}
function strip_txt($h) { return trim(preg_replace('/\s+/u', ' ', html_entity_decode(wp_strip_all_tags((string)$h), ENT_QUOTES | ENT_HTML5))); }
function texts_of($post_id, $source) {
  $raw = get_post_meta($post_id, '_elementor_data', true); $d = is_array($raw) ? $raw : json_decode($raw, true);
  $rows = []; $includes = [];
  if (!$d) return [$rows, $includes];
  els_walk($d, function ($e, $path) use (&$rows, &$includes, $post_id, $source) {
    $w = $e['widgetType'] ?? ''; $s = $e['settings'] ?? []; $id = $e['id'] ?? '';
    $add = function ($field, $text, $tag = null, $extra = []) use (&$rows, $post_id, $source, $id, $w, $path) {
      $t = strip_txt($text); if ($t === '') return;
      $rows[] = array_merge(['post' => $post_id, 'source' => $source, 'el' => $id, 'widget' => $w, 'field' => $field,
        'tag' => $tag, 'text' => $t, 'section' => $path[0] ?? $id], $extra);
    };
    if ($w === 'heading') $add('title', $s['title'] ?? '', $s['header_size'] ?? 'h2');
    if (in_array($w, ['icon-box', 'image-box', 'call-to-action', 'flip-box'])) {
      $add('title_text', $s['title_text'] ?? ($s['title'] ?? ''), $s['title_size'] ?? 'h3');
      $add('description_text', $s['description_text'] ?? ($s['description'] ?? ''), null);
    }
    if (in_array($w, ['text-editor', 'html'])) {
      $f = $w === 'html' ? 'html' : 'editor'; $h = (string)($s[$f] ?? '');
      if (preg_match_all('/<(h[1-6]|p|li|summary)\b[^>]*>(.*?)<\/\1>/is', $h, $m, PREG_SET_ORDER))
        foreach ($m as $x) $add($f, $x[2], strtolower($x[1]), ['inline' => true]);
      if ($w === 'text-editor' && !preg_match('/<(p|h[1-6]|li)\b/i', $h)) $add($f, $h, null);
      if (preg_match_all('/\[elementor-template id="?(\d+)"?\]/', $h, $m)) foreach ($m[1] as $t) $includes[] = (int)$t;
    }
    if ($w === 'shortcode' && preg_match('/\[elementor-template id="?(\d+)"?\]/', $s['shortcode'] ?? '', $m)) $includes[] = (int)$m[1];
    if ($w === 'template' && !empty($s['template_id'])) $includes[] = (int)$s['template_id'];
    if ($w === 'global' && !empty($e['templateID'])) $includes[] = (int)$e['templateID'];
    if (in_array($w, ['nested-accordion', 'n-accordion'])) foreach (($s['items'] ?? []) as $k => $it) $add("items.$k.item_title", $it['item_title'] ?? '', 'summary', ['faq_index' => $k]);
    if (in_array($w, ['accordion', 'toggle'])) foreach (($s['tabs'] ?? []) as $k => $it) {
      $add("tabs.$k.tab_title", $it['tab_title'] ?? '', 'summary', ['faq_index' => $k]);
      $add("tabs.$k.tab_content", $it['tab_content'] ?? '', null, ['faq_index' => $k]);
    }
  });
  return [$rows, array_values(array_unique($includes))];
}
$out = [];
$conds = get_option('elementor_pro_theme_builder_conditions', []);
foreach (array_filter(explode(',', getenv('URLS') ?: '')) as $path) {
  $pid = trim($path, '/') === '' ? (int)get_option('page_on_front') : url_to_postid(home_url($path));
  $pfp = (int)get_option('page_for_posts');
  if (!$pid && $pfp && trailingslashit(wp_parse_url(get_permalink($pfp), PHP_URL_PATH)) === trailingslashit($path)) $pid = $pfp;
  $o = ['path' => $path, 'post' => $pid];
  $rows = []; $inc = [];
  if ($pid) {
    $p = get_post($pid);
    $o += ['type' => $p->post_type, 'status' => $p->post_status, 'title' => $p->post_title,
      'rank_math_title' => get_post_meta($pid, 'rank_math_title', true),
      'rank_math_description' => get_post_meta($pid, 'rank_math_description', true),
      'live_edited' => get_post_meta($pid, '_seo_live_edited', true)];
    [$rows, $inc] = texts_of($pid, 'page');
  }
  $o['theme_templates'] = [];
  foreach ((array)$conds as $loc => $set) if (in_array($loc, ['single', 'archive'])) foreach ((array)$set as $tid => $c) $o['theme_templates'][] = ['id' => (int)$tid, 'location' => $loc, 'conditions' => $c];
  // archives: the posts page (blog) and post-type archives (projects) are drawn by an Elementor archive template;
  // their headings live in that template (shared by every archive page) and their SEO title lives in Rank Math options
  $archive_tpl = function ($needle) use ($conds) { foreach ((array)($conds['archive'] ?? []) as $tid => $c) foreach ((array)$c as $x) if (strpos($x, $needle) !== false) return (int)$tid; return 0; };
  if ($pid && $pid === (int)get_option('page_for_posts')) { $o['kind'] = 'posts_page'; if ($t = $archive_tpl('post_archive')) $inc[] = $t; }
  // a single of a post type drawn by a theme-builder single template (projects, blog posts): its H1 is usually the
  // post title (a dynamic tag), so the post title itself is an editable "heading"
  if ($pid && !in_array($o['type'], ['page'])) {
    foreach ((array)($conds['single'] ?? []) as $tid => $c) foreach ((array)$c as $x)
      if (strpos($x, 'singular/' . $o['type']) !== false) { $inc[] = (int)$tid; $o['kind'] = 'single_template'; }
    $rows[] = ['post' => $pid, 'source' => 'page', 'el' => 'post_title', 'widget' => 'post', 'field' => 'post_title', 'tag' => 'h1', 'text' => get_the_title($pid), 'section' => 'hero'];
  }
  if (!$pid) foreach (get_post_types(['public' => true, 'has_archive' => true], 'names') as $pt) {
    if (trailingslashit(wp_parse_url(get_post_type_archive_link($pt), PHP_URL_PATH)) === trailingslashit($path)) {
      $o['kind'] = 'post_type_archive'; $o['post_type'] = $pt; $o['meta_option'] = "pt_{$pt}_archive_title / pt_{$pt}_archive_description";
      $ro = get_option('rank-math-options-titles', []); $o['rank_math_title'] = $ro["pt_{$pt}_archive_title"] ?? ''; $o['rank_math_description'] = $ro["pt_{$pt}_archive_description"] ?? '';
      if ($t = $archive_tpl($pt . '_archive')) $inc[] = $t;
    }
  }
  $seen = []; $q = $inc;
  while ($q) {
    $t = array_shift($q); if (isset($seen[$t])) continue; $seen[$t] = 1;
    [$r2, $i2] = texts_of($t, 'template:' . $t . ':' . get_the_title($t)); $rows = array_merge($rows, $r2); $q = array_merge($q, $i2);
  }
  $o['includes'] = array_keys($seen); $o['texts'] = $rows; $out[] = $o;
}
echo wp_json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
