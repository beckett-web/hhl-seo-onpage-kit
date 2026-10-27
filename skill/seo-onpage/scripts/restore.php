<?php
/* Roll back a push from its backup folder: puts every post's Elementor data, SEO meta and title back as they were.
   Run:  SCOPE=<scope.json> BACKUP=~/seo-backups/<stamp> wp eval-file restore.php   (scope = the same posts) */
require_once getenv('HOME') . '/hhl-scripts/guard.php';
$dir = getenv('BACKUP'); $n = 0;
if (file_exists("$dir/option-rank-math-options-titles.json")) { g_update_option('rank-math-options-titles', json_decode(file_get_contents("$dir/option-rank-math-options-titles.json"), true)); echo "restored Rank Math archive titles\n"; }
foreach (glob("$dir/[0-9]*.json") as $f) {
  $b = json_decode(file_get_contents($f), true); $p = (int)$b['post'];
  g_update_post_meta($p, '_elementor_data', wp_slash($b['_elementor_data']));
  foreach (['rank_math_title', 'rank_math_description', 'rank_math_focus_keyword'] as $k) g_update_post_meta($p, $k, $b[$k]);
  if (($b['post_title'] ?? '') !== get_the_title($p)) g_update_post(['ID' => $p, 'post_title' => $b['post_title']]);
  delete_post_meta($p, '_elementor_css'); delete_post_meta($p, '_elementor_element_cache'); delete_post_meta($p, '_seo_live_edited'); $n++;
}
if (class_exists('\Elementor\Plugin')) \Elementor\Plugin::$instance->files_manager->clear_cache();
echo "restored $n posts from $dir\n";
