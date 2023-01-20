resource "aws_cloudwatch_event_rule" "trigger_ingest_1min" {
  name                = "Trigger_Ingest_${var.environment}"
  description         = "trigger a lambda ingest job every minute"
  schedule_expression = "cron(*/2 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
  arn       = aws_lambda_function.ingest_lambda.arn
  input     = jsonencode({source_name: "students"})
  rule      = aws_cloudwatch_event_rule.trigger_ingest_1min.name
}

resource "aws_lambda_permission" "allow_cw_to_call_lambda" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest_lambda.function_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.trigger_ingest_1min.arn
}