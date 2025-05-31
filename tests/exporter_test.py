"""
Test cases for the CSV exporter module.
"""

import os
import tempfile
import pandas as pd
import pytest
from md2kg.models import Node, Edge
from md2kg.exporter import CsvExporter


def test_export_basic_nodes_edges():
    """基本的なノードとエッジのCSV出力テスト。"""
    # テスト用のノードとエッジ作成
    nodes = [
        Node(id="node1", title="Document 1", filepath="doc1.md"),
        Node(id="node2", title="Document 2", filepath="doc2.md"),
        Node(id="node3", title="Document 3", filepath="doc3.md"),
    ]
    
    edges = [
        Edge(src_id="node1", dst_id="node2"),
        Edge(src_id="node2", dst_id="node3"),
        Edge(src_id="node1", dst_id="node3"),
    ]
    
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # エクスポーター実行
        exporter = CsvExporter()
        export_result = exporter.export(nodes, edges, tmpdirname)
        
        # ファイルが作成されていることの確認
        nodes_path = os.path.join(tmpdirname, "nodes.csv")
        edges_path = os.path.join(tmpdirname, "edges.csv")
        assert os.path.exists(nodes_path)
        assert os.path.exists(edges_path)
        
        # ファイルの内容検証
        nodes_df = pd.read_csv(nodes_path)
        edges_df = pd.read_csv(edges_path)
        
        # カラム検証
        assert list(nodes_df.columns) == ["id", "title", "filepath", "labels", "tags"]
        assert list(edges_df.columns) == ["src_id", "dst_id", "type", "context_snippet"]
        
        # 行数検証
        assert len(nodes_df) == 3
        assert len(edges_df) == 3


def test_export_with_special_characters():
    """特殊文字を含むデータのCSV出力テスト。"""
    # カンマやクオートを含むタイトル
    nodes = [
        Node(id="node1", title="Document, with comma", filepath="doc1.md"),
        Node(id="node2", title='Document with "quotes"', filepath="doc2.md"),
        Node(id="node3", title="Document \nwith newline", filepath="doc3.md"),
    ]
    
    edges = [
        Edge(src_id="node1", dst_id="node2", context_snippet="Context with, comma and \"quotes\""),
        Edge(src_id="node2", dst_id="node3", context_snippet="Multi\nline\ncontext"),
    ]
    
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # エクスポーター実行
        exporter = CsvExporter()
        export_result = exporter.export(nodes, edges, tmpdirname)
        
        # ファイルが作成されていることの確認
        nodes_path = os.path.join(tmpdirname, "nodes.csv")
        edges_path = os.path.join(tmpdirname, "edges.csv")
        
        # ファイルの内容検証
        nodes_df = pd.read_csv(nodes_path)
        edges_df = pd.read_csv(edges_path)
        
        # データ内容検証
        assert nodes_df.iloc[0]["title"] == "Document, with comma"
        assert nodes_df.iloc[1]["title"] == 'Document with "quotes"'
        
        # エッジの特殊文字データが保持されているか
        assert "comma and" in edges_df.iloc[0]["context_snippet"]


def test_export_tags_and_labels():
    """タグとラベルの出力形式をテスト。"""
    nodes = [
        Node(id="node1", title="Doc with Tags", filepath="doc1.md", 
             tags=["tag1", "tag2", "tag with space"]),
        Node(id="node2", title="Doc with Labels", filepath="doc2.md",
             labels=["Document", "Important"]),
    ]
    
    edges = [
        Edge(src_id="node1", dst_id="node2"),
    ]
    
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # エクスポーター実行
        exporter = CsvExporter()
        export_result = exporter.export(nodes, edges, tmpdirname)
        
        # ノードCSVを読み込み
        nodes_path = os.path.join(tmpdirname, "nodes.csv")
        nodes_df = pd.read_csv(nodes_path)
        
        # タグとラベルの検証
        assert "tag1;tag2;tag with space" == nodes_df[nodes_df["id"] == "node1"]["tags"].iloc[0]
        assert "Document,Important" == nodes_df[nodes_df["id"] == "node2"]["labels"].iloc[0]


def test_export_create_directory():
    """出力先ディレクトリが存在しない場合に自動作成されることをテスト。"""
    nodes = [Node(id="node1", title="Test Doc", filepath="doc.md")]
    edges = []
    
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # 存在しないサブディレクトリを指定
        output_dir = os.path.join(tmpdirname, "subdir", "output")
        
        # エクスポーター実行
        exporter = CsvExporter()
        export_result = exporter.export(nodes, edges, output_dir)
        
        # ディレクトリとファイルが作成されているか確認
        assert os.path.exists(output_dir)
        assert os.path.exists(os.path.join(output_dir, "nodes.csv"))


def test_export_custom_filenames():
    """カスタムファイル名でのエクスポートをテスト。"""
    nodes = [Node(id="node1", title="Test Doc", filepath="doc.md")]
    edges = []
    
    # テスト用の一時ディレクトリ作成
    with tempfile.TemporaryDirectory() as tmpdirname:
        # カスタム名を指定してエクスポート
        exporter = CsvExporter()
        export_result = exporter.export(
            nodes, edges, tmpdirname,
            nodes_filename="custom_nodes.csv",
            edges_filename="custom_edges.csv"
        )
        
        # カスタム名のファイルが存在するか確認
        assert os.path.exists(os.path.join(tmpdirname, "custom_nodes.csv"))
        assert os.path.exists(os.path.join(tmpdirname, "custom_edges.csv"))
