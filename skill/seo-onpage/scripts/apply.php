<?php
/* Apply an approved swap plan (plan.json rows with status ready, plus global rows listed in APPROVE_GLOBAL).
   Run:  SCOPE=<scope.json> PLAN=<plan.json> [APPROVE_GLOBAL=1] [DRY=1] wp eval-file apply.php
   - writes ONLY through guard.php (every post/option must be in the scope file)
   - backs up every post's _elementor_data + SEO meta before its first write (~/seo-backups/<stamp>/<post>.json)
   - keeps a heading's accent <span> on the same number of trailing words
   - on a tag change, rewrites that widget's "selector hN" CSS to the tag-free class so the size stays the same
   - clears Elementor's per-post CSS + element cache, stamps _seo_live_edited so build pipelines skip the page
   - prints one line per row: OK / SKIP / FAIL + why. Read-back of every field is done by verify.py afterwards. */
require_once getenv('HOME') . '/hhl-scripts/guard.php';
$plan = json_decode(file_get_contents(getenv('PLAN')), true);
$dry = getenv('DRY') === '1'; $approve_global = getenv('APPROVE_GLOBAL') === '1';
$stamp = date('Ymd-His'); $bdir = getenv('HOME') . "/seo-backups/$stamp"; if (!$dry) @mkdir($bdir, 0700, true);
// wp eval-file runs this file inside a function: share state through $GLOBALS explicitly, never `global $x` on a local
$GLOBALS['SEO'] = ['dry' => $dry, 'bdir' => $bdir, 'data' => [], 'backed' => []]; $dirty = [];
function load_el($post) { $D = &$GLOBALS['SEO']['data']; if (!isset($D[$post])) { $r = get_post_meta($post, '_elementor_data', true); $D[$post] = is_array($r) ? $r : json_decode($r, true); } return $D[$post]; }
function backup($post) { $S = &$GLOBALS['SEO']; if ($S['dry'] || isset($S['backed'][$post])) return; $S['backed'][$post] = 1;
  if (file_put_contents("{$S['bdir']}/$post.json", wp_json_encode(['post' => $post, '_elementor_data' => get_post_meta($post, '_elementor_data', true),
    'rank_math_title' => get_post_meta($post, 'rank_math_title', true), 'rank_math_description' => get_post_meta($post, 'rank_math_description', true),
    'rank_math_focus_keyword' => get_post_meta($post, 'rank_math_focus_keyword', true), 'post_title' => get_the_title($post)])) === false) throw new Exception("backup failed for $post: stopping before any write"); }
function &find_el(&$els, $id) { $null = null; foreach ($els as &$e) { if (($e['id'] ?? '') === $id) return $e; if (!empty($e['elements'])) { $r = &find_el($e['elements'], $id); if ($r !== null) return $r; } } return $null; }
function norm($t) { $t = strtolower(html_entity_decode(wp_strip_all_tags((string)$t), ENT_QUOTES | ENT_HTML5)); $t = str_replace(['&', '+'], ' and ', $t); $t = preg_replace("/[’'`]/u", '', $t); return trim(preg_replace('/[^a-z0-9]+/', ' ', $t)); }
function with_accent($old, $new) {   // "Why X <span class=..>Choose Elevation</span>" -> wrap the same number of trailing words of the new text
  if (!preg_match('/^(.*?)<span([^>]*)>(.*?)<\/span>\s*([.!?]?)\s*$/s', $old, $m) || trim(wp_strip_all_tags($m[1])) === '') return esc_html($new);
  $k = max(1, count(preg_split('/\s+/', trim(wp_strip_all_tags($m[3]))))); $w = preg_split('/\s+/', trim($new));
  if (count($w) <= $k) return esc_html($new);
  return esc_html(implode(' ', array_slice($w, 0, -$k))) . ' <span' . $m[2] . '>' . esc_html(implode(' ', array_slice($w, -$k))) . '</span>';
}
function pin_size(&$s, $lock, $sel) {   // the size it measured before the tag change, at desktop and phone
  if (!$lock) return; $css = "\n/* seo-onpage: size pinned when the tag changed */\nselector $sel{font-size:{$lock['1440']}px}"
    . "@media (max-width:767px){selector $sel{font-size:{$lock['390']}px}}";
  $s['custom_css'] = ($s['custom_css'] ?? '') . $css; }
function lock_size(&$s, $old_tag) { // widget CSS written against the tag -> against the title class, so a tag change keeps the size
  if (empty($s['custom_css'])) return 0; $n = 0;
  $s['custom_css'] = preg_replace('/selector\s+' . preg_quote($old_tag, '/') . '(?=[\s{,:.\[])/i', 'selector .elementor-heading-title', $s['custom_css'], -1, $n); return $n; }
$res = [];
foreach ($plan as $i => $x) {
  $st = $x['status'] ?? ''; $op = $x['op'] ?? '';
  if (!($st === 'ready' || ($st === 'global' && $approve_global))) { continue; }
  $label = sprintf('#%d %s %s', $i, $x['path'], $x['subject'] ?? $op);
  try {
    if ($op === 'set_meta') {
      $t = $x['target'];
      if ($t['kind'] === 'option') {
        $ro = get_option('rank-math-options-titles', []); [$kt, $kd] = array_map('trim', explode('/', $t['keys']));
        $key = $x['field'] === 'rank_math_title' ? $kt : ($x['field'] === 'rank_math_description' ? $kd : null);
        if (!$key) { $res[] = "SKIP $label: no option for {$x['field']}"; continue; }
        if (!$dry && !file_exists($GLOBALS['SEO']['bdir'] . '/option-rank-math-options-titles.json'))
          file_put_contents($GLOBALS['SEO']['bdir'] . '/option-rank-math-options-titles.json', wp_json_encode(get_option('rank-math-options-titles', [])));
        $ro[$key] = $x['new']; if (!$dry) g_update_option('rank-math-options-titles', $ro); $res[] = "OK   $label: option $key"; continue;
      }
      backup($t['post']); if (!$dry) g_update_post_meta($t['post'], $x['field'], $x['new']); $dirty[$t['post']] = $dirty[$t['post']] ?? false;
      $res[] = "OK   $label: {$x['field']}"; continue;
    }
    $post = (int)$x['post'];
    if ($op === 'heading' && $x['widget'] === 'post') { backup($post); if (!$dry) g_update_post(['ID' => $post, 'post_title' => $x['new']]); $res[] = "OK   $label: post title"; continue; }
    if (!load_el($post)) throw new Exception("post $post has no Elementor data");
    $e = &find_el($GLOBALS['SEO']['data'][$post], $x['el']); if ($e === null) throw new Exception("element {$x['el']} not on post $post (page changed since the plan: re-plan)");
    $s = &$e['settings'];
    if ($op === 'heading') {
      $w = $x['widget']; $tag = $x['tag']; $old_tag = $x['old_tag'];
      if ($x['inline'] ?? false) {
        $f = $x['field']; $h = $s[$f]; $done = false;
        $h2 = preg_replace_callback('/<(' . preg_quote($old_tag, '/') . ')\b([^>]*)>(.*?)<\/\1>/is', function ($m) use ($x, $tag, &$done) {
          if ($done || norm($m[3]) !== norm($x['now'])) return $m[0]; $done = true;
          return "<$tag{$m[2]}>" . with_accent($m[3], $x['new']) . "</$tag>"; }, $h);
        if (!$done) throw new Exception('inline text not found (page changed since the plan)'); $s[$f] = $h2;
      } elseif ($w === 'heading') {
        if (norm($s['title'] ?? '') !== norm($x['now'])) throw new Exception('live text differs from the plan: re-plan');
        $s['title'] = with_accent($s['title'], $x['new']);
        if ($tag !== $old_tag) { $s['header_size'] = $tag; lock_size($s, $old_tag); pin_size($s, $x['lock'] ?? null, '.elementor-heading-title'); }
      } elseif (isset($s['title_text'])) {
        if (norm($s['title_text']) !== norm($x['now'])) throw new Exception('live text differs from the plan: re-plan');
        $s['title_text'] = esc_html($x['new']); if ($tag !== $old_tag) { $s['title_size'] = $tag; pin_size($s, $x['lock'] ?? null, '.elementor-icon-box-title, selector .elementor-image-box-title'); }
      } elseif (preg_match('/^(items|tabs)\.(\d+)\.(item_title|tab_title)$/', $x['field'], $m)) {
        $s[$m[1]][(int)$m[2]][$m[3]] = $x['new'];
      } else throw new Exception("don't know how to edit a {$w} title");
      backup($post); $dirty[$post] = true; $res[] = "OK   $label: \"{$x['now']}\" -> \"{$x['new']}\"" . ($tag !== $old_tag ? " ($old_tag->$tag)" : ''); continue;
    }
    if ($op === 'faq' || $op === 'faq_add') {
      $w = $x['widget']; $ans = $x['answer'] ?? null;
      if (in_array($w, ['nested-accordion', 'n-accordion'])) {
        if ($op === 'faq') { $k = (int)$x['index']; $s['items'][$k]['item_title'] = $x['new'];
          if ($ans) { $set = false;
            $fill = function (&$n) use (&$fill, $ans, &$set) { if (($n['widgetType'] ?? '') === 'text-editor' && !$set) { $n['settings']['editor'] = '<p>' . esc_html($ans) . '</p>'; $set = true; } if (!empty($n['elements'])) foreach ($n['elements'] as &$ch) $fill($ch); };
            $fill($e['elements'][$k]);
            if (!$set) throw new Exception('FAQ answer box not found in that item'); }
        } else {
          if (!$ans) throw new Exception('new FAQ needs an answer');
          $last = end($e['elements']); $s['items'][] = array_merge(end($s['items']), ['item_title' => $x['new'], '_id' => substr(md5(uniqid()), 0, 7)]);
          $fresh = function ($n) use (&$fresh) { $n['id'] = substr(md5(uniqid('', true)), 0, 7); if (!empty($n['elements'])) $n['elements'] = array_map($fresh, $n['elements']); return $n; };
          $copy = $fresh($last); $set = false;
          $fill = function (&$n) use (&$fill, $ans, &$set) { if (($n['widgetType'] ?? '') === 'text-editor' && !$set) { $n['settings']['editor'] = '<p>' . esc_html($ans) . '</p>'; $set = true; } if (!empty($n['elements'])) foreach ($n['elements'] as &$ch) $fill($ch); };
          $fill($copy); if (!$set) throw new Exception('could not find the answer box to copy'); $e['elements'][] = $copy;
        }
      } elseif (in_array($w, ['accordion', 'toggle'])) {
        if ($op === 'faq') { $k = (int)$x['index']; $s['tabs'][$k]['tab_title'] = $x['new']; if ($ans) $s['tabs'][$k]['tab_content'] = '<p>' . esc_html($ans) . '</p>'; }
        else $s['tabs'][] = ['tab_title' => $x['new'], 'tab_content' => '<p>' . esc_html($ans) . '</p>', '_id' => substr(md5(uniqid()), 0, 7)];
      } else throw new Exception("FAQ widget {$w} not supported");
      backup($post); $dirty[$post] = true; $res[] = "OK   $label: FAQ " . ($op === 'faq_add' ? 'added' : 'edited') . " \"{$x['new']}\""; continue;
    }
    $res[] = "SKIP $label: op $op not handled";
  } catch (Throwable $t) { $res[] = "FAIL $label: " . $t->getMessage(); }
  unset($e, $s);
}
foreach ($dirty as $post => $el) {
  if ($el && !$dry) { g_update_post_meta($post, '_elementor_data', wp_slash(wp_json_encode($GLOBALS['SEO']['data'][$post]))); delete_post_meta($post, '_elementor_css'); delete_post_meta($post, '_elementor_element_cache'); }
  if (!$dry) g_update_post_meta($post, '_seo_live_edited', $stamp);
}
if (!$dry && class_exists('\Elementor\Plugin')) \Elementor\Plugin::$instance->files_manager->clear_cache();
echo implode("\n", $res) . "\n" . ($dry ? "DRY RUN: nothing written\n" : "backups: $bdir\n");
