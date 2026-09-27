require_relative "errors"

module Boukensha
  class Registry
    attr_reader :tools

    def initialize
      @tools = {}
    end

    def register_tool(tool)
      @tools[tool.name] = tool
    end

    def tool(name, description:, parameters: {}, &block)
      tool = Tool.new(name.to_s, description, parameters, block)
      register_tool(tool)
      tool
    end

    def dispatch(name, args = {})
      tool = @tools[name.to_s]
      raise UnknownToolError, "No tool registered as '#{name}'" unless tool
      tool.block.call(**args.transform_keys(&:to_sym))
    end
  end
end