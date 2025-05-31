"""
Test cases for the markdown parser module.
"""

import pytest
from md2kg.models import Node, Edge
from md2kg.parser import parse_markdown, _extract_wikilinks


def test_parse_simple_wikilink():
    """単純なWikiLinkを含むMarkdownを解析できること。"""
    markdown_content = """
    # タイトル
    
    これは [[リンク先]] へのWikiLinkを含むテキストです。
    """
    
    # パーサーを実行してノードとエッジを取得
    nodes, edges = parse_markdown("test.md", markdown_content)
    
    assert len(nodes) == 2  # 元ドキュメントとリンク先
    assert len(edges) == 1  # ドキュメント間のリンク
    
    # エッジが正しく生成されているか確認
    assert edges[0].src_id == nodes[0].id  # ソースノードID
    assert edges[0].dst_id == nodes[1].id  # 宛先ノードID
    assert edges[0].type == "LINK"


def test_parse_multiple_wikilinks():
    """複数のWikiLinkを含むMarkdownを解析できること。"""
    markdown_content = """
    # 複数リンクテスト
    
    これは [[リンク1]] と [[リンク2]] への複数のWikiLinkを含むテキストです。
    """
    
    # パーサーを実行
    nodes, edges = parse_markdown("test.md", markdown_content)
    
    assert len(nodes) == 3  # 元ドキュメントと2つのリンク先
    assert len(edges) == 2  # 2つのリンク
    
    # リンク先のタイトルを確認
    link_titles = [node.title for node in nodes[1:]]
    assert "リンク1" in link_titles
    assert "リンク2" in link_titles


def test_parse_wikilink_with_yaml_frontmatter():
    """YAML front-matterを含むMarkdownからtagsを抽出できること。"""
    markdown_content = """---
    tags: ["メモ", "プロジェクト"]
    ---
    
    # YAMLテスト
    
    これは [[リンク先]] へのWikiLinkを含むテキストです。
    """
    
    # パーサーを実行
    nodes, edges = parse_markdown("test.md", markdown_content)
    
    assert len(nodes[0].tags) == 2
    assert "メモ" in nodes[0].tags
    assert "プロジェクト" in nodes[0].tags
    
    # リンク構造も正しく抽出されていることを確認
    assert len(edges) == 1
    assert edges[0].src_id == nodes[0].id


def test_extract_wikilinks():
    """WikiLinksの抽出ロジックが正しく動作すること。"""
    content = "これは [[リンク1]] と [[リンク2]] と [[複雑なリンク名]] を含むテキストです。"
    
    links = _extract_wikilinks(content)
    
    assert len(links) == 3
    assert "リンク1" in links
    assert "リンク2" in links
    assert "複雑なリンク名" in links


def test_empty_markdown():
    """空のMarkdownを解析すると空のリザルトが返ること。"""
    markdown_content = ""
    
    nodes, edges = parse_markdown("empty.md", markdown_content)
    
    assert len(nodes) == 1  # ドキュメント自体のノードのみ
    assert len(edges) == 0  # リンクなし
    assert nodes[0].title == "empty"  # ファイル名がタイトルになる
