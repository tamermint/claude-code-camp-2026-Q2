require_relative "tool"
require_relative "message"


module Boukensha
  class Context
    attr_reader :task, :system, :messages

    def initialize(task:, system: nil)
      @task         = task
      @system       = system
      @messages     = []
    end

    def add_message(role, content, tool_use_id: nil)
      @messages << Message.new(role, content, tool_use_id)
    end

    def turn_count = @messages.size

    def to_s
      "#<Context task=#{task&.task_name} turns=#{turn_count}>"
    end
  end
end