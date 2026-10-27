<?php
/**
 * HHL WRITE GUARD — server side.
 *
 * Every write script must require this FIRST:
 *     require_once __DIR__ . '/guard.php';
 *
 * It reads the approved list from the SCOPE env var:
 *     SCOPE=/home/user/WRITE-SCOPE.json wp ... eval-file ~/fix.php
 *
 * WRITE-SCOPE.json:
 * {
 *   "approved_by": "Beckett",
 *   "what": "swap the service-area map to Fort Myers",
 *   "posts":   [2478, 18, 20],          // post IDs that may be written
 *   "options": ["esci_phone_tel"],      // option names that may be written
 *   "allow_new_posts": false
 * }
 *
 * Then write ONLY through these:
 *     g_update_post_meta($id, $key, $val)
 *     g_update_post($args)
 *     g_update_option($name, $val)
 *     g_set_terms($id, $terms, $tax)
 *
 * Anything not on the list aborts the whole run before it writes.
 */

if (!defined('ABSPATH')) { fwrite(STDERR, "guard: not in WP\n"); exit(1); }

$__scope_file = getenv('SCOPE');
if (!$__scope_file || !file_exists($__scope_file)) {
    WP_CLI::error("WRITE GUARD: no SCOPE file. Set SCOPE=/path/to/WRITE-SCOPE.json.\n"
        . "Nothing was written. Declare which posts you intend to change, get it approved, then re-run.");
}
$GLOBALS['HHL_SCOPE'] = json_decode(file_get_contents($__scope_file), true);
if (!is_array($GLOBALS['HHL_SCOPE'])) WP_CLI::error("WRITE GUARD: SCOPE file is not valid JSON.");

$GLOBALS['HHL_SCOPE'] += ['posts'=>[], 'options'=>[], 'allow_new_posts'=>false, 'what'=>'(unstated)'];
$GLOBALS['HHL_WRITES'] = [];

WP_CLI::log(sprintf("WRITE GUARD active | %s | %d post(s), %d option(s) approved",
    $GLOBALS['HHL_SCOPE']['what'],
    count($GLOBALS['HHL_SCOPE']['posts']), count($GLOBALS['HHL_SCOPE']['options'])));

/* 23 Oct 2026: pages edited through Tamim's seo-onpage kit carry _seo_live_edited. Any OTHER script writing their content or
   SEO fields would silently wipe his SEO work, so those writes stop here. The kit itself runs with SEO_KIT=1; a rebuild that
   must overwrite runs with FORCE_LIVE=1 and then re-applies his last plan. */
function g_check_live($id, $what) {
    if (getenv('SEO_KIT') === '1' || getenv('FORCE_LIVE') === '1') return true;
    $st = get_post_meta($id, '_seo_live_edited', true);
    if ($st) WP_CLI::error(sprintf("WRITE GUARD: post %d (%s) was edited by the SEO kit (%s). Writing its %s would erase that SEO work.\n"
        . "Skip this post, or run with FORCE_LIVE=1 and re-apply the SEO plan after. %d write(s) had already been made.",
        $id, get_the_title($id), $st, $what, count($GLOBALS['HHL_WRITES'])));
    return true;
}
function g_check_post($id) {
    $s = $GLOBALS['HHL_SCOPE'];
    if (in_array((int)$id, array_map('intval', $s['posts']), true)) return true;
    WP_CLI::error(sprintf(
        "WRITE GUARD: post %d is NOT in the approved list.\nApproved: %s\nScope: %s\n"
        . "Run aborted. %d write(s) had already been made, review them.",
        $id, implode(', ', $s['posts']), $s['what'], count($GLOBALS['HHL_WRITES'])));
}
function g_check_option($name) {
    $s = $GLOBALS['HHL_SCOPE'];
    if (in_array($name, $s['options'], true)) return true;
    WP_CLI::error("WRITE GUARD: option '$name' is NOT in the approved list. Run aborted.");
}
function g_update_post_meta($id, $key, $val) {
    g_check_post($id);
    if (in_array($key, ['_elementor_data', 'rank_math_title', 'rank_math_description', 'rank_math_focus_keyword'], true)) g_check_live($id, $key); $GLOBALS['HHL_WRITES'][] = "meta $id.$key";
    return update_post_meta($id, $key, $val);
}
function g_update_post($args) {
    if (!empty($args['ID'])) { g_check_post($args['ID']); if (isset($args['post_title']) || isset($args['post_content'])) g_check_live($args['ID'], 'title/content'); }
    elseif (empty($GLOBALS['HHL_SCOPE']['allow_new_posts']))
        WP_CLI::error("WRITE GUARD: creating a new post needs \"allow_new_posts\": true. Run aborted.");
    $GLOBALS['HHL_WRITES'][] = 'post ' . ($args['ID'] ?? 'NEW');
    return empty($args['ID']) ? wp_insert_post($args) : wp_update_post($args);
}
function g_update_option($name, $val) {
    g_check_option($name); $GLOBALS['HHL_WRITES'][] = "option $name";
    return update_option($name, $val);
}
function g_set_terms($id, $terms, $tax, $append = false) {
    g_check_post($id); $GLOBALS['HHL_WRITES'][] = "terms $id.$tax";
    return wp_set_object_terms($id, $terms, $tax, $append);
}
register_shutdown_function(function () {
    $n = count($GLOBALS['HHL_WRITES'] ?? []);
    if ($n && class_exists('WP_CLI')) WP_CLI::log("WRITE GUARD: $n write(s) made, all in scope.");
});
