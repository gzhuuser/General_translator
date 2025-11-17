import os
import json


class ConfigManager:
    @staticmethod
    def get_config_path():
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(current_dir, "config.json")
    
    @staticmethod
    def save_region(x, y, width, height):
        config = ConfigManager._load_config()
        config.update({
            "x": x,
            "y": y,
            "width": width,
            "height": height
        })
        return ConfigManager._save_config(config)
    
    @staticmethod
    def load_region():
        try:
            config = ConfigManager._load_config()
            return config.get("x", 0), config.get("y", 1121), config.get("width", 2559), config.get("height", 318)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return 0, 1121, 2559, 318
    
    @staticmethod
    def save_user_level(level):
        config = ConfigManager._load_config()
        config["user_level"] = level
        return ConfigManager._save_config(config)
    
    @staticmethod
    def load_user_level():
        try:
            config = ConfigManager._load_config()
            return config.get("user_level", "中级")
        except Exception as e:
            print(f"加载用户水平失败: {e}")
            return "中级"
    
    @staticmethod
    def save_font_size(font_size):
        config = ConfigManager._load_config()
        config["font_size"] = font_size
        return ConfigManager._save_config(config)
    
    @staticmethod
    def load_font_size():
        try:
            config = ConfigManager._load_config()
            return config.get("font_size", 22)
        except Exception as e:
            print(f"加载字体大小失败: {e}")
            return 22
    
    @staticmethod
    def save_zoom_scale(zoom_scale):
        config = ConfigManager._load_config()
        config["zoom_scale"] = zoom_scale
        return ConfigManager._save_config(config)
    
    @staticmethod
    def load_zoom_scale():
        try:
            config = ConfigManager._load_config()
            return config.get("zoom_scale", 100)
        except Exception as e:
            print(f"加载缩放比例失败: {e}")
            return 100
    
    @staticmethod
    def save_llm_config(base_url, api_key, model):
        config = ConfigManager._load_config()
        config["llm"] = {
            "base_url": base_url,
            "api_key": api_key,
            "model": model
        }
        return ConfigManager._save_config(config)
    
    @staticmethod
    def load_llm_config():
        try:
            config = ConfigManager._load_config()
            llm_config = config.get("llm", {})
            return {
                "base_url": llm_config.get("base_url", "https://spark-api-open.xf-yun.com/v1"),
                "api_key": llm_config.get("api_key", ""),
                "model": llm_config.get("model", "4.0Ultra")
            }
        except Exception as e:
            print(f"加载LLM配置失败: {e}")
            return {
                "base_url": "https://spark-api-open.xf-yun.com/v1",
                "api_key": "",
                "model": "4.0Ultra"
            }
    
    @staticmethod
    def _load_config():
        try:
            config_path = ConfigManager.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}
    
    @staticmethod
    def _save_config(config):
        try:
            with open(ConfigManager.get_config_path(), 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
