box.cfg {
    listen = 3301
}
box.once("bootstrap1", function()
    local s = box.schema.space.create('memes')
    s:format({
        { name = 'meme_id', type = 'unsigned' },
        { name = 'top_text', type = 'string' },
        { name = 'bottom_text', type = 'string' },
        { name = 'image_path', type = 'string' },
        { name = 'src_path', type = 'string' }
    })
    box.schema.sequence.create('meme_seq')

    s:create_index('primary', {
        sequence = 'meme_seq',
        type = 'tree',
        parts = { 'meme_id' }
    })

    s:create_index('top_text', {
        type = 'tree',
        unique = false,
        parts = { { field = 'top_text', collation = 'unicode_ci' } }
    })

    s:create_index('bottom_text', {
        type = 'tree',
        unique = false,
        parts = { { field = 'bottom_text', collation = 'unicode_ci' } }
    })
end)

search_top = function(top_text)
    prep = box.prepare([[SELECT * FROM "memes" WHERE "top_text" COLLATE "unicode_ci" LIKE ?;]])
    return prep:execute({ '%' .. top_text .. '%' })
end

search_bottom = function(bottom_text)
    prep = box.prepare([[SELECT * FROM "memes" WHERE "bottom_text" COLLATE "unicode_ci" LIKE ?;]])
    return prep:execute({ '%' .. bottom_text .. '%' })
end

search_meme = function(top_text, bottom_text)
    prep = box.prepare([[SELECT * FROM "memes" WHERE ("top_text" COLLATE "unicode_ci" LIKE ?) AND ("bottom_text" COLLATE "unicode_ci" LIKE ?) ORDER BY (length("top_text")+length("bottom_text")) LIMIT 1;]])
    return prep:execute({ '%' .. top_text .. '%', '%' .. bottom_text .. '%' })
end