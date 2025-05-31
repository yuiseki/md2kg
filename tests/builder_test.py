"""
Test cases for the graph builder module.
"""

import os
import tempfile
import pytest
from md2kg.models import Node, Edge
from md2kg.builder import GraphBuilder


def test_build_from_multiple_files():
    """複数のMarkdownファイルからグラフが正しく構築されること。"""
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # テスト用Markdownファイルを作成
        file1_path = os.path.join(tmpdirname, "doc1.md")
        with open(file1_path, "w") as f:
            f.write("""# Document 1
            
            This links to [[Document 2]].
            """)
        
        file2_path = os.path.join(tmpdirname, "doc2.md")
        with open(file2_path, "w") as f:
            f.write("""# Document 2
            
            This links to [[Document 1]] and [[Document 3]].
            """)
        
        # GraphBuilderのインスタンス化とビルド
        builder = GraphBuilder()
        builder.add_directory(tmpdirname)
        
        # グラフの取得
        nodes, edges = builder.get_graph()
        
        # ノードとエッジの数を検証
        assert len(nodes) == 3  # Document 1, Document 2, Document 3 (存在しないが、リンクされている)
        assert len(edges) == 3  # Doc1->Doc2, Doc2->Doc1, Doc2->Doc3
        
        # ノードタイトルの検証
        node_titles = [node.title for node in nodes]
        assert "Document 1" in node_titles
        assert "Document 2" in node_titles
        assert "Document 3" in node_titles


def test_duplicate_node_merging():
    """重複するノードが正しく統合されること。"""
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # テスト用Markdownファイルを作成 - 互いにリンクする2つのドキュメント
        file1_path = os.path.join(tmpdirname, "source1.md")
        with open(file1_path, "w") as f:
            f.write("""# Common Target
            
            This is the first file with the same title.
            """)
        
        file2_path = os.path.join(tmpdirname, "source2.md")
        with open(file2_path, "w") as f:
            f.write("""# Source
            
            This links to [[Common Target]].
            """)
        
        # GraphBuilderのインスタンス化とビルド
        builder = GraphBuilder()
        builder.add_directory(tmpdirname)
        
        # グラフの取得
        nodes, edges = builder.get_graph()
        
        # 重複ノードが統合されているか検証
        assert len(nodes) == 2  # Source と Common Target の2つだけ
        
        # Common Targetノードはfile1_pathを参照していることを確認
        target_nodes = [node for node in nodes if node.title == "Common Target"]
        assert len(target_nodes) == 1
        assert target_nodes[0].filepath == file1_path


def test_placeholder_nodes():
    """存在しないリンク先がプレースホルダーノードとなること。"""
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # テスト用Markdownファイルを作成
        file_path = os.path.join(tmpdirname, "source.md")
        with open(file_path, "w") as f:
            f.write("""# Source Document
            
            This links to [[Non-existent Document]].
            """)
        
        # GraphBuilderのインスタンス化とビルド
        builder = GraphBuilder()
        builder.add_directory(tmpdirname)
        
        # グラフの取得
        nodes, edges = builder.get_graph()
        
        # ノードが2つ存在することを確認
        assert len(nodes) == 2
        
        # プレースホルダーノードの確認
        placeholder_nodes = [node for node in nodes if node.title == "Non-existent Document"]
        assert len(placeholder_nodes) == 1
        assert placeholder_nodes[0].filepath == ""  # 空のファイルパス
        
        # エッジが正しく作成されていることを確認
        assert len(edges) == 1
        assert edges[0].src_id != edges[0].dst_id


def test_add_file():
    """個別のファイルを追加できること。"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # テスト用Markdownファイルを作成
        file_path = os.path.join(tmpdirname, "single.md")
        with open(file_path, "w") as f:
            f.write("""# Single Document
            
            This is a standalone document.
            """)
        
        # GraphBuilderのインスタンス化
        builder = GraphBuilder()
        builder.add_file(file_path)
        
        # グラフの取得
        nodes, edges = builder.get_graph()
        
        # 1つのノードが存在し、エッジはないことを確認
        assert len(nodes) == 1
        assert nodes[0].title == "Single Document"
        assert len(edges) == 0
